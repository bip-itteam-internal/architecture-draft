## Deskripsi

*Microservice **manufacture-service** — WMS manufaktur (warehouse/produksi): master bahan baku & produk, stok, transaksi in/out, formula/BOM, produksi, material order, PO marketing/procurement, proposal koreksi, dan audit log. Master (bahan, produk, formula) dikelola **native via web** (CRUD penuh). Sync **Google Sheets sudah dihapus** dari service ini — sumber master kini: **bahan & stok dari [[External - Accurate]]** (read-only), **barang jadi & bundle dari data HPP** integration, **formula dari import Excel**. Data operasional (transaksi) **sumber kebenaran di MongoDB**; **angka stok** mengikuti Accurate. Implementasi nyata dari konsep [[Manufacture - Stock & Material Management]].*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/manufacture/*`), auth via header gateway (lihat [[CORE - SSO Flow]]).
- **Path di repo**: `bip-erp/services/manufacture/` · models: `bip-erp/shared-library/models/manufacture/models.go` · FE modul: `erp-frontend/src/features/manufacture/`.
- **Port**: `6978` (`MANUFACTURE_SERVICE_PORT`). **Database**: `manufacture_db` (Mongo per-service, **replica set 1-node** `rs-manufacture` + keyfile auth).
- **Status**: ✅ Implemented (Fase 1 master/stok/transaksi/formula sync jalan; entitas produksi/PO/proposal ada di kode).
- **API**: [[API - Manufacture Service]].

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar rute lengkap di [[API - Manufacture Service]]. Ringkas:

- **Master bahan** — list/detail + CRUD manual (`source:"manual"` → kebal stale-marking) + `PATCH status` + **`POST /master-bahan/sync-accurate`**: tarik master bahan dari Accurate, menggantikan import Excel (`ImportMaster`/`rowsToMaster` sudah dihapus). Filter penting: hanya kode berprefix bahan (`BBK`/`BBO`/`BKK`/`BKO`) **atau** kode yang sudah ada di master — daftar item Accurate juga memuat aset (`PK-` kursi kantor, `PG-` palet), mesin (`PP-` campuran: ALKOHOL & SILLICA GEL bersama MESIN FILLING), sample (`SOT-`) dan barang jadi (`PJ*`). Kategori & satuan di-seed dari prefix **saat insert saja**; tak pernah menghapus.
- **Master produk & bundle** — CRUD manual + **`POST /master-product/sync-hpp`** (barang jadi + mapping bundle dari data HPP integration) + `GET /sku-mapping` (listing SKU → komponen). **Bundle = virtual**: stok hanya ada di level komponen.
- **Stok** — snapshot per kode + `POST /stok/reconcile` (rekonsiliasi snapshot vs transaksi) + `GET /stok/sektor` (stok riil per gudang: utama/tinggar/sadewa, breakdown jenis barang → satuan; konsumen = card Status Sektor di Dashboard FE) + **`POST /stok/sync-accurate`**: stok barang jadi **dan** bahan disamakan dengan Accurate, **READ-ONLY** (WMS tak pernah push balik — belum ada koordinasi manufacture↔finance untuk dua arah).
- **Saldo awal bulanan** — `manufacture_saldo_awal_bulanan`: snapshot stok tiap awal bulan (terpisah dari master barang), dibuat otomatis oleh goroutine ticker (saat boot + tiap 6 jam, idempoten per bulan — service mati saat tanggal 1 terbackfill saat nyala) atau manual via `POST /saldo-awal/snapshot`.
- **Transaksi** — INBOUND/OUTBOUND; mengubah stok **atomik** (Mongo transaction). Validasi kode menerima **master bahan baku ATAU produk jadi** (`master_product`) → transaksi barang jadi (FG in/out) tidak lagi ditolak. OUTBOUND dengan stok tidak cukup ditolak 422 (**stok tidak boleh minus**). `PATCH /transaksi/:id/status` mengubah `detail.status` (alur terima SJ Kirim Produk: IN TRANSIT → DELIVERED). Field UI tambahan (Qty QC, PIC, produk jadi, formula, dll) disimpan apa adanya di field fleksibel `detail`.
- **Formula/BOM** — CRUD penuh (create/update/delete, termasuk `PUT /formula/:id`) + `POST /formula/import` (upload `.xlsx` layout tab NEW FORMULA, upsert by `product_name`). File sumber masih memakai **kode bahan lama (mnemonik)** → dipetakan ke kode kanonik lewat `bahanResolver` (kanonik → alias → nama); kode tak dikenal dilaporkan, tidak dibuang diam-diam.
- **Produksi** — order produksi (konsumsi stok) + production-log (catatan tanpa konsumsi).
- **PO & Proposal** — marketing-po, procurement-po (status workflow + audit), proposal approve/reject. Proposal dipakai untuk **deviasi pemakaian fisik vs teori BOM** pada keluar-produksi: FE membuat proposal `PENDING_PPIC` (transaksi belum ada), approval dua tahap PPIC → SPV; saat `APPLIED` backend insert transaksi + potong stok dengan filter kondisional `stok_sekarang >= qty` (ditolak 409 bila akan minus).
- **Audit log** — `GET /audit-log` (siapa mengubah apa, per aksi/target) + `GET /audit-log/rekap?bulan=YYYY-MM` (agregasi aktivitas CRUD per user untuk **KPI otomatis**; batas hari/bulan pakai **WIB (UTC+7)**, respons ber-flag `truncated` bila entri bulan >20k).
- **Resi — Master Retur Ekspedisi (bridge marketplace)** — `manufacture_resi` (upsert by `no_resi` unik) untuk auto-fill scan form Return & Keluar FG, kini **terisi otomatis** dari order marketplace lewat integration: manufacture bisa **pull** (`POST /resi/sync-tiktok` → `/tiktok/shop/orders/resi-feed`; `POST /resi/sync-shopee` → `/shopee/orders/resi-feed`) atau menerima **push** batch (`POST /resi/sync-batch`) dari scheduler integration `sync-resi-wms` (tiap 10 mnt, watermark per-channel). Tiap resi membawa `status_pesanan`, `tanggal_rts` & `shift` gudang, dihitung saat resi terbuat dari waktu ready-to-ship (WIB): **Shift 1** 08–16 · **Shift 2** 16–24 · **Shift 3** 00–08 (menutup 24 jam; tak ada lagi kategori "Luar Jam"). FE **Master Resi** paginasi **per-hari** (nomor urut reset per hari), filter marketplace + **order status kanonik** (To Process/To Ship/Shipped/Completed/Returned/Cancelled, sama seperti modul Integration) + shift, dan **export Excel** (modal filter + pemilih kolom: Order Id/No Resi/SKU/Nama Produk/Qty + opsional). Detail sisi produsen: [[Microservices - Integration Service]]; jadwal: [[IT - Background Jobs & Schedulers]].

## Model Data (`manufacture_db`)

15 collection (prefix `manufacture_`), grounded ke `models.go`:

- `manufacture_master_bahan` — master bahan baku. `_id` = **kode item Accurate** (`BBO-030`, `BKK-090`), bukan lagi mnemonik internal. Field: `aliases` (kode mnemonik lama, mis. `PEGA` — dipakai importer memetakan file Excel yang masih berkode lama), `faktor_stok_accurate` (pengali qty stok Accurate per-item), nama, kategori, satuan, min_stok, status app-managed, `source:"manual"`.
- `manufacture_master_product` — master produk/bahan kemas (kode, jenis_barang, kategori_produk, status, `source`, `stale`).
- `manufacture_sku_mapping` — mapping listing SKU → komponen (`_id` = listing SKU, `is_bundle`, `components[]{kode,nama,qty}`), di-sync dari HPP. Dasar pemecahan bundle di form Return/Keluar FG.
- `manufacture_stok` — snapshot stok per kode (bahan **dan** barang jadi). Angkanya ditimpa `POST /stok/sync-accurate`.
- `manufacture_transaksi` — transaksi in/out + `detail` (bson.M, field UI tambahan).
- `manufacture_formula` — resep/BOM (product_name + ingredients[kode_bahan, nama, qty_needed]); `kode_bahan` menunjuk kode kanonik master bahan.
- `manufacture_sync_log` — riwayat sync/import (tipe: `master_bahan_sync_accurate`, `stok_sync_accurate`, `sync_hpp`, `formula_import`).
- `manufacture_production_log` (+`detail`) · `manufacture_material_order` · `manufacture_marketing_po` · `manufacture_procurement_po` (+`detail`, menampung daftar `items` saat 1 permintaan berisi banyak bahan) · `manufacture_proposal`.
- `manufacture_saldo_awal_bulanan` — snapshot saldo awal per bulan (`_id` = `kode|YYYY-MM`, kode, nama, bulan, qty) — memisahkan saldo awal bulanan dari data master barang.
- `manufacture_audit_log` — jejak perubahan oleh user (dari header `BIP-Employee-ID`/`BIP-Username`).
- `manufacture_resi` — master resi/AWB retur ekspedisi (`no_resi` **unik**, `nama_market`, `nama_toko`, `nomor_pesanan`, `status_pesanan`, `tanggal_pesanan`, `tanggal_rts`, `shift`, `ekspedisi`, `items[]{sku,nama_barang,qty_total}`) — sumber auto-fill scan form Return & Keluar FG. **Terisi otomatis** dari order TikTok/Shopee via resi-bridge (upsert by `no_resi`), tak lagi bergantung input manual.

## Keputusan Teknis (grounded)

- **Stok = opening-balance-as-transaction + reconcile**: mutasi stok pakai **Mongo multi-document transaction** (butuh replica set; itu sebab `manufacture_db` dijadikan RS 1-node + keyfile). Catatan: sejak stok bahan & barang jadi di-sync dari Accurate, **snapshot tak lagi murni "jumlah semua transaksi"** — sync menimpanya dengan angka Accurate; transaksi WMS menyesuaikan stok di antara dua sync.
- **Sumber master pindah dari Google Sheets ke Accurate/HPP**: sync Sheets **dihapus** dari service (tak ada lagi pemanggilan Sheets API; `source:"sheet"` tak dipakai). Bahan & stok ← Accurate, barang jadi & bundle ← data HPP integration, formula ← import Excel. ⚠️ Sisa: env `SHEETS_SA_KEY` **masih disuntikkan** ke `Manufacture-Service` di `docker-compose.dev.yml` padahal kodenya tak membacanya lagi (config mati, aman dihapus).
- **Kode bahan = kode item Accurate** (bukan mnemonik internal): kode lama disimpan di `aliases`. Perlu karena file Excel formula MASIH memakai kode lama — tanpa pemetaan alias, tiap import menghidupkan kembali kode lama dan memutus rujukan ke stok Accurate. Resolusi importer: kanonik → alias → **nama** (fallback nama sekaligus menyembuhkan kode rusak akibat parsing Excel, mis. `1,2` terbaca `1`).
- **Konversi satuan stok Accurate (wajib, bukan kosmetik)**: Accurate menyimpan **bahan curah dalam KG** sedangkan WMS memakai **GRAM** (formula `qty_needed` juga gram). Tanpa konversi ×1000, sync "berhasil" tapi diam-diam mengecilkan stok bahan 1000× dan perhitungan kebutuhan produksi ikut salah. Dasar: rasio stok_lama(GRAM)/qty_accurate untuk 178 bahan bermedian **1002** (kuartil 966–1056); PCS/LITER/ROL/KG berasio ~1. `accurate_stocks` **tidak membawa satuan**, jadi satuan diambil dari master bahan WMS.
- **Faktor stok per-item dipisah dari satuan** (`faktor_stok_accurate`, menang atas aturan satuan): ada bahan yang satuan Accurate-nya tak bisa disimpulkan dari satuan WMS — mis. `BBO-056` CANGKANG KAPSUL, Accurate memakai **ribuan butir** sedangkan WMS memakai PCS (faktor 1000). Menandainya `GRAM` cuma demi memicu ×1000 memang membuat angka MRP benar, tapi labelnya salah (kapsul terhitung sebagai bahan curah bergram di dashboard) — karena itu faktor dibuat eksplisit dan bisa diatur via `PUT /master-bahan/:kode`.
- **Tagged logging** `[Manufacture <Event>]` untuk identifikasi di monitoring Docker.
- **Audit log** merekam user login terakhir yang mengubah data di tab mana pun (header gateway).
- **Field `detail` (bson.M) sebagai blob fleksibel**: model Go inti (transaksi, production-log, procurement-po) minimal, sedangkan UI punya banyak field tambahan (QC, PIC, checklist, daftar bahan). Field tersebut disimpan apa adanya di `detail` agar log/ledger/arsip tetap utuh setelah reload — tanpa menambah kolom per-field di model.
- **Item master manual kebal sync**: master-bahan **dan master-product** buatan WMS (`source:"manual"`) dikecualikan dari penandaan `stale` saat sync, jadi tidak hilang. Sync bersifat **upsert murni** — kode yang tak ada di sumber dibiarkan, tak pernah dihapus.
- **Mapping gudang = per-master** (tidak ada kolom gudang per baris): kode master bahan = **Gudang Utama** (bahan baku+kemas); kode master barang = **Gudang Tinggar** (kemas+barang jadi); **Gudang Sadewa** (titipan) dihitung dari net transaksi bergudang-simpan "sadewa". Kode yang terdaftar di dua master terhitung di dua gudang (aproksimasi; stok per-gudang sejati masih TBD).
- **Aturan stok & approval keluar-produksi**: stok **tidak boleh minus** (blokir di FE + validasi 422 backend + filter kondisional saat proposal APPLIED). Approval PPIC→SPV terpicu oleh **deviasi fisik pemakaian vs teori BOM** (bukan oleh kekurangan stok).
- **Rantai alur FE saling tereferensi & anti-duplikat**: keluar-produksi membuat `grupDokumen` (RM-OUT-BOM) → Laporan Hasil Produksi mengambil grup (menyimpan `grupDokumen`; grup terpakai disembunyikan) & Qty Masuk Gudang menciptakan stok FG (`PROD-<batch>`) → Kirim Produk mengambil laporan (menyimpan `refLaporanProduksi`; laporan terpakai disembunyikan; OUTBOUND, SJ IN TRANSIT) → Input Gudang FG menerima SJ (PATCH status DELIVERED; INBOUND + gudang simpan Utama/Tinggar/Sadewa) → Masuk Kembali mengembalikan sisa bahan per grup via checklist. 
- **Akses modul WMS**: halaman `/manufacture` dibatasi system role `manufacture` (guard FE `ManufactureGuard`), supervisor IT super-akses; tombol approve di menu Persetujuan & Akun mengikuti role `manufacture: ppic`/`supervisor` dari cookie `system_roles` (verifikasi role backend belum ada — lihat temuan audit).
- **FE**: modul `manufacture` di [[APP - Web ERP]] (Next.js, `erp-frontend/src/features/manufacture`), 10 view (gudang bahan baku/jadi, stok, produksi, PO, KPI, dll). Fitur terbaru: tab **Master Barang** kini **CRUD produk penuh** (badge sumber Manual/Sheet), kartu **Formula BOM** punya tombol edit; modul **Pusat Laporan & KPI** menambah tab **KPI Otomatis (rekap CRUD)** — skor per user dari audit log (indikator berbobot ala menu KPI Scoring, batas WIB, prorate bulan berjalan); menu **Audit History** dipisah tab **Ledger Transaksi** vs **Log Aktivitas User** + pagination + filter tanggal. Konversi field **dua arah**: tulis (legacy camelCase → Go snake_case + `_id`), baca (Go snake_case → legacy camelCase) lewat mapper di container — tanpa ini create gagal validasi (`id`/`product_sku` wajib) & arsip tampil kosong.

## Belum Diimplementasikan / Catatan (TBD)

- Perhitungan kebutuhan→kekurangan otomatis dari rencana produksi (Fase 2 di [[Manufacture - Stock & Material Management]]) — sebagian (formula ada, planning belum penuh).
- Multi-gudang/lokasi + karantina ED, stock opname digital — masih konsep.
- **Integrasi [[External - Accurate]] baru SATU ARAH (read)**: WMS membaca stok, tak pernah push balik. Dua arah ditunda sampai ada koordinasi manufacture↔finance (risiko dobel-hitung bila WMS & finance sama-sama menulis).
- **8 kode bahan belum diselaraskan** ke kode Accurate — ambigu, sengaja tidak ditebak: `SLG` (Accurate salah ketik `PP-036 SILLICA GEL`), `PS SRK 7/8/9/10/12 CM` (nama "PLASTIK SRING", Accurate punya varian ukuran+merek yang tak terputuskan otomatis — fuzzy match sempat salah pilih 9→19 CM dan 10/12→20 CM), `RF150` (BOTOL VIVIDENT 150 ML, tak ada di Accurate), `TEST-01` (data testing). Dilaporkan tiap sync via `bahan_tanpa_padanan_accurate`.
- **`#N/A` di formula** DR FAY SERUM & HAIR & BODY WASH — error di file NEW FORMULA sumber, bukan bug kode.
- Env `SHEETS_SA_KEY` masih diteruskan ke Manufacture-Service di compose walau kodenya tak memakainya lagi (config mati).
- **Temuan audit kode** (authz, race stok, mapper FE, seed atomik) terdaftar di [[Manufacture - Issue Code Audit 2026-06]] — perbaikan terjadwal.

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] (routing + inject header identitas) · [[CORE - SSO Flow]] (auth).
- [[Microservices - Employee Service]] — sumber identitas/role (audit).
- [[GA - Procurement System]] — kekurangan → pengadaan (rencana).
- [[External - Accurate]] — **sumber master bahan & angka stok (read-only)**, diakses lewat [[Microservices - Integration Service]] (`/accurate/stocks/list`, salinan lokal `accurate_stocks`); manufacture tak pernah memanggil Accurate langsung. Lihat [[ADR - 0001 Akuntansi via Accurate]].
- [[Microservices - Integration Service]] — data HPP (barang jadi & bundle) + resi-feed marketplace.

## Dokumen Terkait

- [[Manufacture - Stock & Material Management]] (konsep/desain) · [[API - Manufacture Service]] (endpoint)
- [[DB - Overview and Notes]] · [[APP - Web ERP]]

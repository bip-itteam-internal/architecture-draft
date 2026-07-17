## Deskripsi

*Endpoint **manufacture-service** (WMS manufaktur: master bahan/produk, stok, transaksi, formula, produksi, PO, proposal, resi retur ekspedisi). Gateway: `/api/manufacture/*`. Grounded ke `services/manufacture/main.go`.*

- **Implementasi**: [[Microservices - Manufacture Service]] · **Status**: ✅ (di kode)
- **Indeks**: [[API - Index]] · RBAC: di-handle di gateway (tak eksplisit di rute).

## Master & stok
| Method | Path | Fungsi |
|---|---|---|
| GET | `/master-bahan` · `/master-bahan/:kode` | List/detail master bahan |
| POST/PUT/DELETE | `/master-bahan` · `/master-bahan/:kode` | Create/update/delete master bahan manual (tandai `source:"manual"` → kebal stale-marking saat sync). PUT juga menyetel `faktor_stok_accurate` (pengali qty stok Accurate per-item; 0 = pakai aturan satuan) |
| POST | `/master-bahan/sync-accurate` | **Tarik master bahan dari Accurate** (via integration `/accurate/stocks/list`) — menggantikan import Excel. Hanya kode berprefix bahan (`BBK`/`BBO`/`BKK`/`BKO`) **atau** kode yang sudah ada di master; daftar item Accurate juga memuat aset (`PK-` kursi, `PG-` palet), mesin (`PP-` campuran), sample (`SOT-`) & barang jadi (`PJ*`) yang tak boleh masuk master bahan. Nama diperbarui dari Accurate; kategori & satuan di-seed dari prefix **saat insert saja**; `min_stok`/`lokasi`/`aliases` milik WMS. Tak pernah menghapus. **Tak pernah menduplikasi**: bila bahan yang sama sudah ada dengan kode lama (nama cocok), insert dilewati & pasangannya dilaporkan di `perlu_align` — jalankan align dulu |
| POST | `/master-bahan/align-accurate` (`?dry_run=true`) | **Migrasi kode bahan lama → kode Accurate**, sekali per environment. Memindahkan `_id` + cascade seluruh rujukan (stok, saldo awal ber-`_id` komposit, transaksi, formula, production-log, material-order, procurement-po); merge bila >1 kode lama menunjuk 1 kode Accurate; menyembuhkan rujukan formula rusak lewat nama. Idempoten. Pencocokan **hanya nama sama persis** — yang tak cocok dibiarkan & dilaporkan (jangan ditebak: fuzzy match pernah memilih "PLASTIK SHRINK 19 CM" untuk "PLASTIK SRING 9 CM"). `dry_run` menampilkan rencana tanpa menyentuh data |
| PATCH | `/master-bahan/:kode/status` | Ubah status master bahan (audit) |
| GET | `/master-product` · `/master-product/:kode` | List/detail master produk |
| POST/PUT/DELETE | `/master-product` · `/master-product/:kode` | Create/update/delete master produk manual (tandai `source:"manual"` → kebal stale-marking saat sync) |
| POST | `/master-product/sync-hpp` | Tarik barang jadi + mapping bundle dari data HPP integration (`/profit/wms/finished-products` & `/profit/wms/sku-mappings`); upsert murni, tak menyentuh non-PRODUK-JADI |
| POST | `/master-product/align-hpp` (`?dry_run=true`) | **Migrasi kode produk jadi lama → master_sku HPP** (mis. `NEI` → `PJB-001`), kembaran align bahan. Kanonik = kode di HPP **atau** daftar item Accurate (18 produk di luar HPP — `BRL`, `F001`, dst. — sah, tak dipindah). Cascade: stok, saldo awal, transaksi (+`detail.sku`), production-log (+`detail`), material/marketing PO, formula.product_sku, `resi.items[].sku`. Idempoten; pencocokan hanya nama sama persis |
| GET | `/sku-mapping` (`?bundle=true`) | Mapping listing SKU → komponen. Bundle bersifat **virtual**: stok hanya ada di level komponen |
| GET/POST | `/stok` · `/stok/:kode` · `/stok/reconcile` | Stok + rekonsiliasi |
| POST | `/stok/sync-accurate` | **Sync stok barang jadi + bahan dari Accurate — READ-ONLY** (WMS tak pernah push balik; lihat [[ADR - 0001 Akuntansi via Accurate]]). Hanya kode yang terdaftar di master. **Konversi satuan** wajib: bahan `GRAM` ×1000 (Accurate menyimpan bahan curah dalam KG), plus `faktor_stok_accurate` per-item bila satuan Accurate tak bisa disimpulkan dari satuan WMS (mis. cangkang kapsul: Accurate memakai ribuan butir, WMS memakai PCS). Melaporkan `bahan_tanpa_padanan_accurate`, `satuan_perlu_dicek` (satuan PCS tapi qty Accurate pecahan) & `stok_dikonversi` |
| POST | `/stok/align` (`?dry_run=true`) | **Bersihkan baris stok & saldo awal yatim** (kode tak ada di master bahan maupun barang — lahir dari DeleteMaster yang tak menghapus stok, atau sisa data test). Tak tampil di UI tapi berbahaya laten: mutasi stok pakai `$inc`, kode yang dibuat ulang mewarisi angka basi. Idempoten |
| GET | `/stok/sektor` | Stok riil per gudang untuk card Status Sektor (utama = kode master bahan, tinggar = kode master barang, sadewa = net transaksi bergudang-simpan "sadewa"); breakdown `jenis` → satuan → qty. Terdaftar **sebelum** `/stok/:kode` agar tidak tertangkap param |
| GET/POST | `/saldo-awal` (`?bulan=YYYY-MM`) · `/saldo-awal/snapshot` (`?force=true`) | Saldo awal bulanan (snapshot stok tiap awal bulan, terpisah dari master); snapshot idempoten — dipicu otomatis (boot + ticker 6 jam) atau manual. `force=true` = buang snapshot **bulan berjalan** lalu potret ulang dari stok terkini — dipakai sesudah stok pindah sumber ke Accurate (snapshot lama berisi angka era sebelumnya dan idempotensinya membuat ia tak pernah memperbaiki diri) |

## Transaksi · Formula · Produksi
| Method | Path | Fungsi |
|---|---|---|
| GET/POST | `/transaksi` | List/buat transaksi stok (INBOUND/OUTBOUND); kode boleh master bahan **atau** produk jadi (`master_product`); OUTBOUND ditolak 422 bila stok tidak cukup; field UI tambahan (QC, PIC, dll) disimpan apa adanya di `detail` |
| PATCH | `/transaksi/:id/status` | Ubah status UI transaksi (`detail.status`) — dipakai alur terima SJ Kirim Produk (IN TRANSIT → DELIVERED) |
| POST | `/transaksi/fg` | Transaksi barang jadi multi-baris: **validasi seluruh baris dulu, baru tulis** (tak ada tulisan separuh jalan bila satu baris stoknya kurang). Baris bundle dipecah ke komponen lewat `/sku-mapping` |
| GET/POST/PUT/DELETE | `/formula` · `/formula/:id` | Formula/BOM (resep produksi) — CRUD penuh (create/update/delete) |
| POST | `/formula/import` | Import formula/BOM dari file `.xlsx` (multipart `file`, layout tab NEW FORMULA), upsert by `product_name`. File utama `NEW FORMULA.xlsx` (di C:/Work, mesin user) **sudah dikonversi ke kode Accurate** (16 Juli 2026; 832 kode diganti, tersisa 2 sel `#N/A` error sumber) — tapi salinan lama yang beredar masih bisa memakai kode mnemonik → importer tetap memetakan lewat alias → nama; kode tak dikenal dilaporkan di `kode_bahan_tak_dikenal` |
| GET/POST | `/production` | Order produksi (konsumsi stok) |
| GET/POST/DELETE | `/production-log` · `/production-log/:id` | Catatan produksi (tanpa konsumsi stok) |
| GET/POST/DELETE | `/material-order` · `/material-order/:id` | Order material internal |

## Resi — Master Retur Ekspedisi
| Method | Path | Fungsi |
|---|---|---|
| GET | `/resi` · `/resi/lookup/:resi` | List semua resi · lookup 1 resi by `no_resi` (auto-fill scan form Return & Keluar FG). Tiap resi bawa `status_pesanan`, `tanggal_rts`, `shift` — diturunkan dari waktu ready-to-ship (WIB): **Shift 1** 08–16 · **Shift 2** 16–24 · **Shift 3** 00–08 |
| POST/PUT/DELETE | `/resi` · `/resi/:id` | CRUD resi (mayoritas terisi otomatis; tombol input manual sudah dihapus dari UI, endpoint tetap ada) |
| POST | `/resi/sync-tiktok` | **Pull** resi order TikTok dari integration `/tiktok/shop/orders/resi-feed`, upsert by `no_resi` (index unik) |
| POST | `/resi/sync-shopee` | **Pull** resi order Shopee dari integration `/shopee/orders/resi-feed`, upsert by `no_resi` |
| POST | `/resi/sync-batch` | **Push endpoint**: menerima batch resi-feed dari scheduler integration `sync-resi-wms` (lihat [[IT - Background Jobs & Schedulers]]) |

## PO · Proposal · Audit
| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PATCH/DELETE | `/marketing-po` · `/marketing-po/:id[/status]` | PO marketing (audit) |
| GET/POST/PATCH/DELETE | `/procurement-po` · `/procurement-po/:id[/status]` | PO procurement (audit) |
| GET/POST | `/proposal` · `/proposal/:id/approve` · `/reject` | Proposal koreksi/deviasi pemakaian fisik (PENDING_PPIC → PENDING_SPV → APPLIED, audit). Saat APPLIED, pemotongan stok memakai filter kondisional `stok_sekarang >= qty` — ditolak 409 bila akan membuat stok minus |
| GET | `/audit-log` (`?user=&aksi=`) · `/audit-log/rekap` (`?bulan=YYYY-MM`) · `/health` | Audit log (list) · rekap aktivitas CRUD per user/bulan untuk **KPI otomatis** (agregasi batas hari/bulan pakai **WIB**, respons ber-flag `truncated` bila >20k entri) · health |

## Dokumen Terkait
- [[Microservices - Manufacture Service]] · [[Manufacture - Stock & Material Management]] · [[GA - Procurement System]] · [[API - Integration Service]] (resi-feed) · [[IT - Background Jobs & Schedulers]] (`sync-resi-wms`) · [[API - Index]]

## Deskripsi

*Menu **Material Order (MO)** — lembar **SPK formula** produksi. Admin memilih produk jadi + target qty, sistem menurunkan kebutuhan tiap bahan dari formula/BOM (`qty_needed_per_unit × target_qty`) berikut stok terkininya, lalu hasilnya disimpan dan dicetak sebagai SPK. MO adalah **hulu rantai No. Batch**: nomor batch yang ditulis di MO-lah yang kemudian dipilih di [[Manufacture - Dokumen Produksi Batch]] dan diteruskan ke Laporan Produksi. MO **tidak menyentuh stok** — pengeluaran bahan yang sesungguhnya tetap lewat transaksi OUTBOUND di menu RM Keluar ke Produksi.*

- **Stack**: Go + Fiber v2 + MongoDB (backend), Next.js/React + TypeScript (frontend)
- **Path (backend)**: `bip-erp/services/manufacture/material_order.go`; rute di `main.go:232-234`; model di `shared-library/models/manufacture/models.go` (`MaterialOrder`, `MaterialOrderIngredient`)
- **Path (frontend)**: `erp-frontend/src/features/manufacture/components/MaterialOrderView.tsx` (sub-tab `material_order`); mapper & pemanggil API di `manufacture-app.tsx` (`mapMaterialOrderToLegacy`, `handleAddMaterialOrder`, `handleDeleteMaterialOrder`); tipe di `types/legacy.ts`
- **Menu**: Manufacture (WMS) → grup **Order & Dokumen** → **Material Order & PO** (`/manufacture/orders-po`), sub-tab **SPK Material Order (Formula)**. Dua sub-tab tetangganya (**PO Marketing**, **Permintaan Pengadaan**) entitas terpisah, bukan bagian MO.
- **Status**: ⚠️ Implemented (ada catatan) — dipakai harian dan menyuapi dossier batch, tapi tanpa edit, tanpa status/approval, dan penomorannya dibuat acak di browser. Lihat **Catatan & Belum Diimplementasikan**.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC (`system_roles`) | Device |
|---|---|---|---|
| Admin Produksi | Manufaktur — produksi | `manufacture = admin_produksi` — buat, cetak, hapus SPK | Desktop web |
| Admin Gudang RM | Manufaktur — gudang RM | `manufacture = admin_gudang_rm` — sama | Desktop web |
| Admin Gudang FG | Manufaktur — gudang FG | `manufacture = admin_gudang_fg` — sama | Desktop web |
| PPIC / SPV | Manufaktur | super-akses seluruh tab WMS (`wmsSuperAccess`) | Desktop web |
| Procurement | Procurement | `system_roles.procurement` — **read-only di FE saja**, backend belum mencerminkannya (lihat Catatan) | Desktop web |

- **Tujuan**: menggantikan hitungan kebutuhan bahan manual (spreadsheet) dengan penurunan otomatis dari BOM, sekaligus menerbitkan lembar SPK yang dipegang produksi.
- **Pain point (cara lama)**: kebutuhan bahan dihitung tangan per target produksi, tak ada arsip SPK, dan No. Batch tak terikat ke dokumen mana pun.
- **Aksi utama**: pilih produk jadi → isi target qty + No. Batch + PIC → tinjau tabel kebutuhan vs stok → simpan → cetak SPK.

> Gerbang tab `orders_po` (baca **dan** tulis memakai daftar role yang sama) ada di `services/manufacture/rbac.go:69` (`matriksTabWMS`), dicerminkan FE di `features/manufacture/akses.ts:48`. Latar RBAC WMS: [[Microservices - Manufacture Service]] & [[CORE - RBAC dan Permission Set]].

## Fitur (Sudah Diimplementasikan)

### Penurunan kebutuhan dari formula
- Produk jadi dipilih lewat pencarian (cocok by `sku` **atau** `name`); formula dicocokkan by `productSku`/`productName`.
- Tiap bahan formula dihitung `qty_needed_per_unit × target_qty` = `qty_needed_total`, disandingkan dengan `current_stock` dari master + snapshot stok, lalu ditandai cukup/tidak (`isSufficient`). Perhitungan ini terjadi di **browser** (`MaterialOrderView.tsx:205-225`).
- **Varian Formula 1/2**: pilihan resep hanya muncul bila produk memang punya Formula 2 (`formulaHasVariant2`), sesuai perilaku menu operasional lain. Lihat [[Manufacture - Stock & Material Management]].

### Arsip & cetak
- Panel **SPK hari ini** menyaring MO ber-`tanggal` sama dengan hari ini, di samping **Arsip SPK Material Order** berisi seluruh MO terurut terbaru.
- Cetak SPK memakai `KopSurat` + lembar A4 yang dipaksa terang di kedua tema lewat `PAPER_LIGHT_VARS` (pola yang sama dengan PO Marketing & Permintaan Pengadaan, lihat [[APP - Web ERP]]).

### Rantai ke dokumen produksi
- [[Manufacture - Dokumen Produksi Batch]] menarik sendiri `GET /material-order` (`BatchRecordView.tsx:134-162`) untuk membangun: daftar No. Batch yang **belum dipakai** dossier mana pun, peta `no_batch → {kode_bahan → qty_needed_total}` (kolom **MO** di Rekonsiliasi MO), dan detail produk + bahan untuk auto-isi dossier. Pencocokan No. Batch dinormalisasi `trim().toUpperCase()`.
- Rincian rantai `MO → Dokumen Produksi → Laporan Produksi` dan menu **Rekonsiliasi MO** ada di dok itu; sengaja **tidak** diulang di sini.

### Audit & stempel penginput
- `created_by_name` **distempel server** dari header `BIP-Username`, nilai dari body selalu ditimpa. `admin_pic` berbeda: field bisnis yang diketik di form. Aturan lengkapnya di [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]].
- Create & delete menulis `manufacture_audit_log` (`CREATE_MATERIAL_ORDER` / `DELETE_MATERIAL_ORDER`).

## Model Data

Koleksi `manufacture_material_order`, struct `MaterialOrder` (`shared-library/models/manufacture/models.go:530`):

| Field (BSON) | Tipe | Keterangan |
|---|---|---|
| `_id` | string | Nomor MO, **dikirim client** (bukan ObjectId) |
| `tanggal` | string | `YYYY-MM-DD` |
| `product_sku` · `product_name` | string | Produk jadi sasaran |
| `target_qty` | float64 | Target produksi (PCS di UI) |
| `admin_pic` | string | PIC yang diketik manual di form |
| `ingredients[]` | `MaterialOrderIngredient` | `sku` · `nama` · `qty_needed_per_unit` · `qty_needed_total` · `current_stock` · `unit` |
| `no_batch_reference` | string (opsional) | No. Batch — **kunci sambung ke dossier batch** |
| `keterangan` | string (opsional) | Catatan bebas; disisipi teks `[Formula 2]` bila varian 2 dipakai |
| `metadata` | `common.Metadata` | `created_by` = employee_id |
| `created_by_name` | string (opsional) | Nama penginput, stempel server |

Tidak ada field status, approval, maupun revisi. Bandingkan dengan `MarketingPO` (punya `realisasi_qty`) dan `Proposal` (punya alur PPIC→SPV) di [[Microservices - Manufacture Service]].

## Endpoint

Semua di belakang [[CORE - API Master Gateway]] dengan prefix `/api/manufacture`. Daftar lengkap service: [[API - Manufacture Service]].

| Method | Path | Gerbang | Keterangan |
|---|---|---|---|
| GET | `/material-order` | `requireTabRead("orders_po")` | Seluruh koleksi, **tanpa filter & tanpa paginasi** (`bson.M{}`) |
| POST | `/material-order` | `requireTabWrite("orders_po")` | Wajib `_id` & `product_sku` saja; `ingredients` boleh kosong |
| DELETE | `/material-order/:id` | `requireTabWrite("orders_po")` | 404 bila `DeletedCount == 0` |

## Catatan & Belum Diimplementasikan

- **Tak ada endpoint update.** Hanya GET/POST/DELETE (`main.go:232-234`); MO salah ketik harus dihapus lalu dibuat ulang, dan penghapusannya tak memeriksa apakah `no_batch_reference`-nya sudah dipakai dossier.
- **Tak ada status/approval.** MO langsung final begitu disimpan. Berbeda dari batch record (DRAFT→DIAJUKAN→LULUS) dan proposal koreksi (PPIC→SPV).
- ⛔ **`_id` dan `no_batch_reference` di-generate di browser dengan `Math.random()`** — `MO-2026-<4 digit>` dan `BATCH-<tahun>/<3 digit>` (`MaterialOrderView.tsx:156, 252`), bukan sequence server. Tabrakan `_id` gagal keras (duplicate key → 500), tapi **`no_batch_reference` tidak unik dan tak divalidasi di mana pun**, padahal dossier memakainya sebagai kunci pilih. Dua MO ber-No. Batch sama **menyatu diam-diam** di `BatchRecordView.tsx:141-156`: dropdown hanya menampilkan satu entri, `qty_needed_total` per bahan **dijumlahkan** dari kedua MO, sementara detail auto-isinya diambil dari MO yang **terakhir** dibaca. Hasilnya kolom MO di Rekonsiliasi MO bisa memuat angka gabungan yang tak cocok dengan lembar SPK mana pun, tanpa satu pun pesan galat. Ruang nomornya hanya 900 nilai per tahun.
- **`qty_needed_total` dihitung frontend, server menyimpan apa adanya.** `CreateMaterialOrder` hanya `BodyParser` lalu insert — tak pernah menghitung ulang dari `manufacture_formula`. Angka yang kelak jadi `teoritis` di dossier berasal dari perhitungan browser, jadi perubahan formula setelah MO terbit tidak tercermin dan tak ada yang membandingkannya.
- **Varian Formula 2 hanya jejak teks.** Ditulis sebagai `[Formula 2]` yang disisipkan ke `keterangan` (`MaterialOrderView.tsx:260`), bukan field terstruktur — konsumen hilir tak bisa mengetahui varian resep secara programatik.
- ⚠️ **Read-only Procurement belum bergerbang di backend.** FE memasukkan `orders_po` ke `TAB_WMS_PROCUREMENT` (`akses.ts:148`) sehingga pemegang `system_roles.procurement` melihat menunya, tapi `rbac.go` tak punya cerminannya: `tabFinanceReadOnly` hanya memuat `finished_goods`, `substitusi`, `piutang_konsinyasi`, dan `tabViewerReadOnly` hanya `finished_goods`. Menurut pembacaan kode, akun Procurement **tanpa** role `manufacture` akan kena 403 di `GET /material-order` — dan 403 itu **ditelan** jadi daftar kosong oleh `.catch(() => emptyList)` di `manufacture-app.tsx:531`, persis kelas kegagalan yang dicatat di `rbac.go:167`. Belum diverifikasi lewat akun sungguhan. Kelas yang sama berlaku untuk `TAB_WMS_QUALITY`/`TAB_WMS_RND` di tab lain.
- **`tanggal` dibentuk dari `toISOString()` (UTC), bukan tanggal WIB.** MO yang dibuat antara 00:00–07:00 WIB tercatat sebagai hari sebelumnya. Panel "SPK hari ini" memakai rumus yang sama sehingga tetap konsisten dengan dirinya sendiri, tapi tanggal yang tersimpan bukan tanggal kerja. Bandingkan konvensi hari di [[Sales - Marketing Dashboard (Analisis Rekap)]].
- **Perhitungan kekurangan → pengadaan masih TBD** — MO menandai bahan yang stoknya kurang di layar, tapi tak ada jalur otomatis ke [[GA - Procurement System]]. Lihat [[Manufacture - Stock & Material Management]] dan [[Manufacture - Issue Material Miss Count]].

## Dependensi & Integrasi

- [[Microservices - Manufacture Service]] — service induk, koleksi, dan gerbang RBAC WMS
- [[Manufacture - Dokumen Produksi Batch]] — konsumen utama `no_batch_reference` + `qty_needed_total`
- [[Manufacture - Stock & Material Management]] — formula/BOM, varian Formula 1/2, perencanaan kebutuhan
- [[APP - Web ERP]] — menu, akses lintas-modul, dan pola cetak
- [[External - Accurate]] — asal master bahan & angka stok yang tampil di kolom stok (read-only)

## Dokumen Terkait

- [[API - Manufacture Service]] · [[Manufacture - Order Production Workflow (Flow Source)]] (flowchart Work Order & BOM di sisi Accurate, hulu konseptual MO)
- [[Manufacture - Issue Code Audit 2026-06]] · [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]
- [[CORE - API Master Gateway]] · [[CORE - RBAC dan Permission Set]]

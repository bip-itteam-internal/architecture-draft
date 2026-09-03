# ADR - 0069 Perlengkapan Per-Unit Opsional di `inventory` dengan Guard Anti-Kontaminasi

## Untuk Manajemen

- **Yang berubah di layar**: perlengkapan **durable** (charger, mic, tripod, APAR) kini **diinput di Kelola Aset seperti aset tetap**, lalu **dipadankan ke item perlengkapan Accurate** (by nama) lewat Pengaturan Aset. Jumlah barang yang terpadan **mengisi otomatis** kolom Hitung Fisik di tab opname, tetap bisa dikoreksi.
- **Siapa terdampak**: staff GA. Barang massal (pulpen/tisu) TETAP kuantitas/hitung manual — per-unit hanya untuk barang yang layak dilacak satuan.
- **Tidak dijanjikan**: perlengkapan **tidak** disusutkan (akun 1606, bukan aktiva tetap), **tidak** menggantikan opname manual (keduanya berdampingan; prefill cuma memudahkan), dan pemegang **opsional** (barang fasilitas umum tak berpemegang).
- **Besaran kerja**: sedang. Reuse model unit + plumbing padanan aset tetap; yang baru: field padanan sendiri, endpoint hitung unit, editor, dan **guard agar perlengkapan tak mencemari angka aset tetap**.

## Deskripsi

*Memperluas [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] / [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]]: perlengkapan boleh menjadi **unit per-item** di koleksi `inventory` (bukan hanya angka di `ga_stok`), dipadankan ke **item Accurate** (`item_no`, many-to-one). Menembus batas model lama secara SADAR, dijaga guard anti-kontaminasi. Melengkapi [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] — jumlah unit memprefill Hitung Fisik.*

- **Status**: ✅ **Implemented** (2026-09-01). Landasan opname: ADR-0067; padanan aset: ADR-0037/0049.
- **Path di repo**: BE `bip-erp/services/inventory` (`InventoryItem.AccurateItemNo`, PATCH `accurate_item_no` di `validation.go`, guard opex di `penyusutan.go`, `perlengkapan_unit.go` count/list), `shared-library/models/inventory/models.go`; FE `erp-frontend/src/features/inventory` (`perlengkapan-pairing.tsx` editor pasang-saja, `use-perlengkapan-units.ts`, prefill `perlengkapan-opname-tab.tsx`).
- **Tanggal**: 2026-09-01

## Context

Opname perlengkapan (ADR-0067) mengukur akurasi per-KUANTITAS: staff GA mengetik hitung fisik vs qty Accurate. Staff meminta perlengkapan **durable** (charger/mic/APAR — namanya sudah memuat lokasi/pemegang) bisa dipadankan **per-unit** seperti aset tetup, dan hitung fisiknya **terisi otomatis** dari unit yang sudah dipadankan.

Keadaan terukur (grounded):

- Model lama **sengaja** memisahkan: FASS = per-unit di `inventory`; perlengkapan = **angka di `ga_stok`** ("500 pulpen sebagai FASS melahirkan 500 dokumen", `models.go:162-185`). Perlengkapan **tidak** punya baris unit.
- Accurate melacak perlengkapan sebagai **KUANTITAS** (`item_no` + qty; mis. Palet 85, APAR 2) — beda "sisi" dari register aktiva tetap (`accurate_asset_no`). Jadi padanan per-unit = **many-to-one** (N unit ERP → satu `item_no`).
- Konsumen `inventory` berisiko-tinggi: **`GetPenyusutan → opex insentif` (UANG)** dan **KPI `akurasi_aset_ga`** (menarik `/items`); keduanya kini mengasumsikan semua isi `inventory` = FASS.

## Decision

> **Koreksi arah (2026-09-01)**: iterasi pertama sempat memisahkan perlengkapan (field `sifat`
> + guard FASS-only di banyak konsumen + editor buat-unit). Pemilik produk mengoreksi: **campur
> saja seperti aset tetap, cuma jangan masuk opex** — jadi keputusan di bawah yang berlaku.

1. **Perlengkapan diinput sebagai `InventoryItem` lewat Kelola Aset BIASA** (`POST /item`, persis cara input aset tetap — tanpa toggle/jenis), lalu **dipadankan by-NAMA** ke item perlengkapan Accurate → **`accurate_item_no`** (via `PATCH /item/:id`). Field padanan **TERPISAH** dari `accurate_asset_no` (register aset tetap).
2. **Perlengkapan CAMPUR dengan aset tetap** di koleksi `inventory`, `GET /items`, dan ringkasan — **TIDAK dipisah, TIDAK ada field `sifat`**. Diskriminator "ini perlengkapan" = **keberadaan `accurate_item_no`** (dipadankan ke item perlengkapan Accurate).
3. **SATU-SATUNYA pengecualian: penyusutan (opex).** `GetPenyusutan` mengecualikan item ber-`accurate_item_no` — perlengkapan akun 1606 bukan aktiva tetap, jadi tak boleh masuk biaya opex insentif pemegang. Dikunci test.
4. **Padanan = editor PASANG-SAJA** (cerminan `AsetPairingEditor`, sisi Accurate diganti `accurate_stocks`): pilih barang ERP + item perlengkapan Accurate → simpan `accurate_item_no`. Bukan editor buat-unit.
5. **Prefill opname**: jumlah barang ERP ber-`accurate_item_no`=`<item_no>` (endpoint `/perlengkapan-units/count`) **memprefill** Hitung Fisik (bulan berjalan, tetap bisa dikoreksi + Simpan). Berdampingan dengan opname manual (ADR-0067).

## Consequences

- **Positif**: input & pengalaman **persis aset tetap** (satu form, satu daftar); padanan by-nama seragam; prefill opname otomatis; reuse penuh model/holder/soft-delete; **pengecualian minimal (satu guard opex)** → permukaan kontaminasi kecil & terlokalisir.
- ⚠️ **KPI Fase 2 WAJIB menangani ini**: karena perlengkapan **campur** di `/items` (yang ditarik KPI `akurasi_aset_ga`), dan ia tak punya `accurate_asset_no`, ia akan dinilai **100% (ERP-only)** → menggelembungkan skor aset tetap. Saat Fase 2, `akurasi_aset_ga` **wajib mengecualikan** item ber-`accurate_item_no` (perlengkapan dinilai lewat metrik opname sendiri). **Belum masalah** — KPI belum attach ke template mana pun. ✅ **FE 2026-09-03**: tab Cocokkan (`reconcile-tab`) sudah mengecualikan item ber-`accurate_item_no` dari daftar + skor/cakupan/kpiScore yang DITAMPILKANNYA (erp-frontend `fix/cocokkan-perlengkapan-dan-filter`; diskriminator `itemPerlengkapan` di `utils/reconcile.ts`). Ini menutup kontaminasi di layar; BE `akurasi_aset_ga` (yang menarik `/items`) **tetap Fase 2**.
- **Ongkos**: field `accurate_item_no` + jalur PATCH-nya, endpoint count/list, editor padanan, prefill.
- **Ditunda**: **KPI perlengkapan** (metrik opname sendiri + exclude dari `akurasi_aset_ga`); **assign pemegang nyata** (perlengkapan pakai jalur serah-terima aset yang sudah ada); **auto-padan dari penerimaan pembelian**; **barang massal per-unit** (pulpen/tisu tetap kuantitas `ga_stok`).
- **Gotcha ke `review-checklist.md`**: koleksi bersama dengan diskriminator — konsumen yang lupa menyaring bisa mencemari uang/KPI. Di sini yang dijaga cuma opex; KPI Fase 2 yang menyusul adalah PR-nya sendiri.

## Dokumen Terkait

- [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] · [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]] · [[GA - Inventory Management]] · [[Microservices - Inventory Service]] · [[External - Accurate]]

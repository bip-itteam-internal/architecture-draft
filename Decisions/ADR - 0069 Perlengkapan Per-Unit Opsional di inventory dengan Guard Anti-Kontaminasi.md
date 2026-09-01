# ADR - 0069 Perlengkapan Per-Unit Opsional di `inventory` dengan Guard Anti-Kontaminasi

## Untuk Manajemen

- **Yang berubah di layar**: perlengkapan **durable** (charger, mic, tripod, APAR) kini bisa **didaftarkan per-unit** & **dipadankan ke item Accurate** lewat Pengaturan Aset — seperti aset tetap. Jumlah unit yang terdaftar **mengisi otomatis** kolom Hitung Fisik di tab opname, tetap bisa dikoreksi.
- **Siapa terdampak**: staff GA. Barang massal (pulpen/tisu) TETAP kuantitas/hitung manual — per-unit hanya untuk barang yang layak dilacak satuan.
- **Tidak dijanjikan**: perlengkapan **tidak** disusutkan (akun 1606, bukan aktiva tetap), **tidak** menggantikan opname manual (keduanya berdampingan; prefill cuma memudahkan), dan pemegang **opsional** (barang fasilitas umum tak berpemegang).
- **Besaran kerja**: sedang. Reuse model unit + plumbing padanan aset tetap; yang baru: field padanan sendiri, endpoint hitung unit, editor, dan **guard agar perlengkapan tak mencemari angka aset tetap**.

## Deskripsi

*Memperluas [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] / [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]]: perlengkapan boleh menjadi **unit per-item** di koleksi `inventory` (bukan hanya angka di `ga_stok`), dipadankan ke **item Accurate** (`item_no`, many-to-one). Menembus batas model lama secara SADAR, dijaga guard anti-kontaminasi. Melengkapi [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] — jumlah unit memprefill Hitung Fisik.*

- **Status**: ✅ **Implemented** (2026-09-01). Landasan opname: ADR-0067; padanan aset: ADR-0037/0049.
- **Path di repo**: BE `bip-erp/services/inventory` (`InventoryItem.Sifat`+`AccurateItemNo`, guard `ListInventory`/`GetSummary`/`GetPenyusutan`, `perlengkapan_unit.go`), `shared-library/models/inventory/models.go`; FE `erp-frontend/src/features/inventory` (`perlengkapan-pairing.tsx`, `use-perlengkapan-units.ts`, prefill `perlengkapan-opname-tab.tsx`).
- **Tanggal**: 2026-09-01

## Context

Opname perlengkapan (ADR-0067) mengukur akurasi per-KUANTITAS: staff GA mengetik hitung fisik vs qty Accurate. Staff meminta perlengkapan **durable** (charger/mic/APAR — namanya sudah memuat lokasi/pemegang) bisa dipadankan **per-unit** seperti aset tetup, dan hitung fisiknya **terisi otomatis** dari unit yang sudah dipadankan.

Keadaan terukur (grounded):

- Model lama **sengaja** memisahkan: FASS = per-unit di `inventory`; perlengkapan = **angka di `ga_stok`** ("500 pulpen sebagai FASS melahirkan 500 dokumen", `models.go:162-185`). Perlengkapan **tidak** punya baris unit.
- Accurate melacak perlengkapan sebagai **KUANTITAS** (`item_no` + qty; mis. Palet 85, APAR 2) — beda "sisi" dari register aktiva tetap (`accurate_asset_no`). Jadi padanan per-unit = **many-to-one** (N unit ERP → satu `item_no`).
- Konsumen `inventory` berisiko-tinggi: **`GetPenyusutan → opex insentif` (UANG)** dan **KPI `akurasi_aset_ga`** (menarik `/items`); keduanya kini mengasumsikan semua isi `inventory` = FASS.

## Decision

1. **Perlengkapan boleh jadi `InventoryItem` per-unit** ber-`sifat=perlengkapan` + **`accurate_item_no`** (padanan ke item Accurate). Field padanan **TERPISAH** dari `accurate_asset_no` (register aset tetap) — pakai ulang akan mencemari join & skor rekonsiliasi/KPI aset tetap.
2. **Masuk koleksi `inventory` bersama aset tetap** (reuse penuh model/holder/soft-delete), BUKAN koleksi terpisah — DENGAN **4 guard**:
   - **`sifat` didenormalisasi ke unit** (aman: sifat immutable) → guard jadi filter field sederhana.
   - **`ListInventory` (`/items`), `GetSummary`, `GetPenyusutan` default FASS-only** (`sifat != perlengkapan`). KPI `akurasi_aset_ga` menarik `/items` → **otomatis terlindungi**.
   - **Perlengkapan TAK PERNAH disusutkan** (exclude di `GetPenyusutan`).
   - **Test regresi = penjaga utama**: unit perlengkapan tak menggeser angka aset tetap.
3. **Pemegang opsional** (fallback "Tersedia di GA"); barang fasilitas umum (APAR) tak berpemegang.
4. **Berdampingan dengan opname manual (ADR-0067), bukan mengganti**: jumlah unit **memprefill** Hitung Fisik (hanya bulan berjalan, tetap bisa dikoreksi + Simpan). Barang tanpa unit → manual (hibrida per-barang).

## Consequences

- **Positif**: alat & pengalaman "seperti aset tetap"; opname durable jadi otomatis; satu koleksi (reuse penuh).
- **Risiko yang diredam**: kontaminasi angka uang/KPI aset tetap — dijaga guard + test regresi.
- ⚠️ **Risiko sisa yang tak terhapus tuntas**: **konsumen `/items` BARU di masa depan** yang lupa menyaring `sifat` akan re-mengontaminasi. Gotcha ini dinaikkan ke `review-checklist.md`. Denormalisasi `sifat` ke unit + default FASS-only meminimalkannya, tapi disiplin review tetap perlu.
- **Ongkos**: field baru, endpoint hitung/list unit, editor padanan, prefill.
- **Ditunda**: **KPI perlengkapan** (ikut jalur `akurasi_aset_ga`, jangan sumber ketiga); **assign pemegang nyata** unit (v1 held_by kosong); **auto-daftar unit dari penerimaan pembelian**; **barang massal per-unit** (tetap kuantitas).

## Dokumen Terkait

- [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] · [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]] · [[GA - Inventory Management]] · [[Microservices - Inventory Service]] · [[External - Accurate]]

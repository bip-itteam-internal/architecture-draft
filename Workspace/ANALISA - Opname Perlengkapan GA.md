# ANALISA - Opname Perlengkapan GA

Analisa kebutuhan (pra-`/plan`). Keputusan arsitekturalnya di [[ADR - 0065 Opname Perlengkapan GA via Rekonsiliasi Accurate]]; konsep domainnya di [[GA - Inventory Management]].

**Dibuat**: 2026-08-31 · **Status**: keputusan terkunci, beberapa parameter ditunda ke `/plan` (§4).

---

## 0. Kebutuhan vs solusi yang diusulkan

**Solusi yang diusulkan user**: "tarik data perlengkapan dari Accurate, tampilkan di tab **Perlengkapan** baru di modul Aset GA."

**Kebutuhan sebenarnya** (digali): staff GA melakukan **stock opname** perlengkapan (hitung fisik) dan org ingin **mengukur akurasinya → KPI** — persis paralel dengan **rekonsiliasi aset tetap** yang sudah ada, bukan fitur berdiri sendiri.

Selisih solusi↔kebutuhan yang penting:
- "Tab Perlengkapan baru" → **tidak perlu**. Masuk ke tab **Data Accurate** yang ada, lewat pemilih tipe.
- "Sekadar tampilkan data Accurate" → **tidak cukup**. Referensi pasif tak menghasilkan angka akurasi; opname menuntut **input hitung fisik**.

## 1. Yang sudah ada (grounded)

| Sudah ada | Bukti |
|---|---|
| Data perlengkapan Accurate tersinkron di sisi kita | `accurate_stocks` (integration_db), cron 30 mnt + webhook, `accurate_stock.go`; 904 item; `GET /accurate/stocks/list` (0 call Accurate saat render) |
| Pola rekonsiliasi GA↔Accurate + skor akurasi | [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]], [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]] — tapi baru untuk aset tetap |
| Tab "Data Accurate" (penjelajah aset tetap Accurate) | `erp-frontend .../accurate-data-tab.tsx` (`useFixedAssets`) |
| Konsep perlengkapan berbasis kuantitas | `models.go` `GaStok` + `SifatPerlengkapan`/`SifatFASS`; koleksi `ga_stok`; alur Permintaan Barang GA (`TambahStokFisik`) |

## 2. Yang BELUM ada (jadi kerja baru)

1. **Kategori item di `accurate_stocks`.** Skema `{item_no, name, qty}` — tanpa kategori. Prefix `item_no` **bukan** pemisah bersih (terukur prod: BBK 177, BKK 161, angka 128, BKO 85, PP 70, dst). → sync harus **menangkap kategori Accurate**.
2. **Store record hitung fisik opname.** Aset tetap menyimpan kunci padanan (`accurate_asset_no`) di item; opname perlengkapan butuh record tersendiri (item · qty_fisik · snapshot qty_accurate · tanggal · oleh siapa · selisih).
3. **Padanan berbasis kuantitas.** Skor aset tetap = harga/tanggal; skor opname = **kecocokan qty fisik vs Accurate** (variance).
4. **FE**: pemilih tipe `Aset Tetap`/`Perlengkapan` di tab Data Accurate (menukar tabel+kolom) + form input opname + kolom selisih.

## 3. Keputusan terkunci (→ ADR 0065)

- **Bentuk**: alat opname AKTIF — GA input hitung fisik.
- **Acuan/kebenaran**: **fisik vs qty Accurate** (Accurate = buku Finance). `ga_stok` = kolom pembanding, bukan kebenaran.
- **KPI**: masuk (paralel Fase 2 aset tetap).
- **Penempatan**: tab **Data Accurate**, **pemilih tipe** Aset Tetap/Perlengkapan (tukar tabel+kolom). **Bukan** tab baru, **bukan** mencampur ke tabel aset tetap.

**Diputuskan TIDAK dibangun**: tab "Perlengkapan" terpisah · modul opname berdiri sendiri · referensi pasif · `ga_stok` sebagai kebenaran · perlengkapan sebagai aset per-unit di koleksi `inventory`.

## 4. TBD untuk `/plan` (bukan untuk analisa)

- Formula skor akurasi opname + **toleransi variance** (perlengkapan qty pecahan mungkin, mis. liter).
- **Periode opname** (bulanan? per-permintaan?) dan bagaimana snapshot qty Accurate dipatok saat opname.
- Apakah opname **ikut meng-update `ga_stok`** atau murni pengukuran (hindari `ga_stok` jadi sumber kedua yang menyimpang).
- Apakah **kategori "Perlengkapan" Accurate cukup bersih** — filter nama staff GA di Accurate (kecualikan *alkohol/alpha/hexa/niacinamide*) menyiratkan kategori saja mungkin belum memisahkan bahan baku sepenuhnya. Cek dari file hasil `z-file-hasil/general-affair/kuantitas_barang_per_gudang_*.xlsx` saat `/plan`.

## Dokumen Terkait

- [[ADR - 0065 Opname Perlengkapan GA via Rekonsiliasi Accurate]] · [[GA - Inventory Management]] · [[Microservices - Integration Service]] · [[Microservices - Inventory Service]] · [[External - Accurate]]

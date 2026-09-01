## ADR 0049 — Padanan Aset ERP↔Accurate per-item berbasis NAMA (menggantikan kategori→golongan)

- **Status**: ✅ Accepted — **FE Implemented (2026-08-22)** di `erp-frontend` (branch `feat/aset-repair-nota`, sudah merge `main`); **mirror BE KPI (Fase 2) belum**. **Menggantikan sebagian [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]]** (§2 jembatan kategori→golongan; §3 golongan sebagai faktor skor).
- **Konteks dok**: [[GA - Inventory Management]] · [[Microservices - Inventory Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- **ADR terkait**: [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]

## Context

[[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] memakai pemetaan **kategori-ERP → golongan-Accurate** (`faType`, mis. "Peralatan Kantor") sebagai jembatan: tab Cocokkan mengelompokkan aset per golongan, `suggestMatch` menyaring kandidat ke golongan sama, dan skor field menilai harga + tanggal + **golongan**.

Dua fakta membuat pendekatan itu terbukti keliru:

- **Golongan terlalu kasar.** Laptop dan gorden sama-sama `faType` "Peralatan Kantor". `suggestMatch` versi lama **mengabaikan nama** dan hanya memilih segolongan + **harga terdekat**, sehingga laptop bisa disarankan/tersimpan padanan ke gorden. Sebagian data `accurate_asset_no` lama tercemar salah-pasang.
- **Nama aset Accurate kini tersedia.** Sebelumnya salinan lokal `accurate_fixed_assets` mengisi `Nama` dari `faType.name` (golongan), sehingga semua "Peralatan Kantor" — pencocokan by nama mustahil. Setelah nama sebenarnya diambil dari field **`description`** Accurate (lihat [[Microservices - Integration Service]]), pencocokan by nama menjadi mungkin dan lebih tepat.

## Decision

**Rekonsiliasi berpindah dari "kategori→golongan + skor golongan" ke "padanan per-item berbasis NAMA".**

1. **Editor "Pengaturan Aset" diganti** dari kategori→golongan menjadi **padanan langsung barang ERP → aset Accurate** (`aset-pairing.tsx`): pilih barang ERP (combobox cari **nama + kategori**, kategori = merk/brand), pilih aset Accurate (combobox cari **kode + nama**, tampil `kode · nama`), Simpan menyimpan `accurate_asset_no` pada item — **jalur penyimpanan yang sama** dengan tab Cocokkan (`PATCH /item/:id`, `useConfirmMatch`).
2. **`suggestMatch` memeringkat by kemiripan NAMA** (tumpang-tindih token) lebih dulu; harga jadi penyeimbang. `namaScore` + `padananMencurigakan` di `reconcile.ts`.
3. **Padanan lama yang salah ditandai, tidak dihapus otomatis.** Padanan tersimpan yang **nol tumpang-tindih nama** ditandai ⚠ "Periksa padanan" + baris "mungkin lebih tepat: …" + tombol **"Ganti ke saran"** (satu-klik menimpa ke padanan benar). Staff memutuskan per item.
4. **Skor rekonsiliasi/KPI tidak lagi menilai golongan.** `computeFieldScore` hanya menilai **kesamaan DATA**: harga (toleransi 1%) + tanggal — 2 faktor berbobot sama. Rumus persentase (akurasi/cakupan, ERP-only=100%) tetap seperti ADR-0037.

**Yang ditolak:**
- **Mempertahankan golongan sebagai kunci pencocokan/skor.** Terbukti memasangkan barang beda-jenis; nama lebih tepat sejak nama Accurate ada.
- **Melepas otomatis padanan mencurigakan.** Netting/hapus massal berisiko membuang yang benar; ditandai saja, staff yang mengganti.

## Consequences

**Diterima:**
- Padanan akurat berdasarkan nama; data lama yang salah **terlihat** (⚠) dan mudah dibetulkan satu-klik.
- Skor jujur mengukur kesamaan data ERP↔Accurate, bukan kelas aset.
- Reuse penuh penyimpanan `accurate_asset_no` — editor Pengaturan Aset & tab Cocokkan menulis kunci yang sama (dua pintu, satu kebenaran).

**Ongkos / catatan (GAP):**
- **`asset_category_mapping` (kategori→golongan) jadi vestigial**: koleksi + rute `/category-mapping` tetap ada dan **masih dibaca tab Cocokkan** untuk pengelompokan saran (data lama), tetapi **tak ada lagi UI menambah** pemetaan baru. Bila ingin memindahkan Cocokkan sepenuhnya ke padanan langsung, perlu rework tersendiri (belum).
- **Mirror BE KPI (Fase 2) belum disamakan.** `ComputeFieldScore` versi Go di `shared-library` + sumber `akurasi_aset_ga` ([[Microservices - Employee Service]]) **masih menilai golongan** dan **belum di-deploy** — wajib membuang faktor golongan saat KPI otomatis dirilis, konsisten dengan butir Decision #4.

**Amandemen 2026-09-01 — kuantitas & harga per-unit pakai basis CURRENT.** `computeFieldScore` membagi `biaya_perolehan ÷ kuantitas` untuk harga per-unit. Dua fakta yang semula hanya hidup sebagai komentar Go (aturan "kolom yang butuh kalimat pemakaian wajib naik ke dok", review-checklist §G2) dan sempat salah dipahami saat perancangan: **(1)** `detail.do.quantity` = kuantitas **perolehan awal** yang TIDAK pernah turun saat pelepasan; kuantitas current ada di **`quantityAvailable`**. **(2)** `AssetCost`/`biaya_perolehan` **basis current** (ikut turun saat disposal). Terbukti prod APK-073 2026-09-01: perolehan 4×1,15jt = 4,6jt, disposisi 2 unit −2,3jt → `AssetCost` 2,3jt, `quantityAvailable` 2 → 1,15jt/unit. Karena itu ERP kini memetakan `kuantitas` dari `quantityAvailable` (bukan `quantity`) agar **basis biaya & kuantitas sama** — mencampurnya (`biaya current ÷ qty perolehan` = 2,3jt÷4 = 575rb) menggeser skor per-unit 2×. Aset `kuantitas==0` (habis dilepas) disembunyikan di tab Data Accurate. Grounded: `integration/.../accurate_client_aset_tetap.go` (`QuantityAvailable`), `aset_tetap_refresh.go` (`petakanAsetTetap`), `frontend/.../accurate-data-tab.tsx`; detail endpoint di [[API - Integration Service]].

## Dokumen Terkait

- [[GA - Inventory Management]] · [[Microservices - Inventory Service]] · [[API - Inventory Service]]
- [[Microservices - Integration Service]] · [[External - Accurate]]
- [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]

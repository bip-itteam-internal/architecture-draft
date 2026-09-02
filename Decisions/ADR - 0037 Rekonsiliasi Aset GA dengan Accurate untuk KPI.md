## ADR 0037 — Rekonsiliasi Aset GA ↔ Accurate: ceklis per-item untuk KPI, matrix per-golongan untuk kesehatan data

- **Status**: ⚠️ Accepted — **SEBAGIAN DI-SUPERSEDE oleh [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]]** (2026-08-22): **§2 jembatan kategori→golongan** dan **§3 golongan sebagai faktor skor** DIGANTI oleh padanan per-item berbasis NAMA + skor tanpa golongan. Yang TETAP berlaku: ceklis per-item, ERP-only=100%, atribusi `created_by`, penempatan (inventory menyimpan `accurate_asset_no`, FE mengomposisi, feed KPI lewat employee-service).
- **Status Fase (pra-0049)**: **Fase 0 & 1 Implemented** (2026-08-06): `accurate_asset_no`/`reconciled_at` + koleksi `asset_category_mapping` + rute `/category-mapping` ([[Microservices - Inventory Service]]); FE tab reconcile client-side. **Fase 2 (feed KPI): kode di branch `feat/kpi-akurasi-aset`, belum merge/deploy** — sumber KPI `akurasi_aset_ga` di [[Microservices - Employee Service]] (jalur [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]); **sisa non-kode**: konfigurasi metrik `kpi_template` GA (label/bobot) + env `INVENTORY_MODULE_URL`/`INTEGRATION_MODULE_URL` saat deploy. **Catatan: skor Fase 2 masih memakai golongan → wajib disamakan ke ADR-0049 (buang golongan) saat rilis.**
- **Konteks dok**: [[GA - Inventory Management]] · [[Microservices - Inventory Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- **ADR terkait**: [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0002 Database-per-Service]]

## Context

HRGA meminta metrik KPI untuk **posisi staff GA**: kualitas input aset di modul Aset ERP diukur dengan **membandingkannya terhadap data padanan di Accurate**. Makin cocok, makin tinggi skor; sepadan penuh = 100%. Pertanyaan pokoknya: **apa padanan "aset ERP" di Accurate, bagaimana mencocokkannya, dan bagaimana skornya jatuh ke orang secara adil** — tanpa mengulang ongkos yang sudah dibayar di tempat lain.

Fakta yang membatasi jawaban (grounded):

- **Aset GA di ERP ≠ stok/persediaan.** [[Microservices - Inventory Service]] eksplisit "asset tracking, bukan stok-kuantitas gudang" (`services/inventory`). Item punya `master_data.item_category` yang **bebas-ketik** (disimpan apa adanya, dedup case-insensitive; dropdown dihapus), `purchase_price` **opsional**, dan **nilai buku dihitung frontend sebagai estimasi** garis lurus — bukan angka pembukuan. Service ini `InternalURL` kosong: **tidak memanggil service lain**.
- **Penginput aset terekam.** `CreateInventory` mengisi `metadata.created_by` = `employee_id` dari klaim login (`common.UpsertMetadata`, `services/inventory/controller.go`) — jadi skor **dapat dibebankan per staff GA** (fondasi atribusi Fase 2). Menjawab kekhawatiran "pemetaan karyawan belum memadai" di [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] untuk kasus aset GA.
- **Padanan Accurate-nya adalah Aktiva Tetap, dan pembacanya SUDAH ADA.** integration-service menyimpan **salinan lokal** `accurate_fixed_assets` (Mongo), disegarkan **cron harian + trigger manual**, disajikan `GET /accounting/fixed-assets` + `/accounting/fixed-assets/summary` (lihat [[API - Integration Service]] §Accounting-FAT). Entity `entity.AsetTetap` sudah memodelkan — dari probe Accurate hidup, bukan tebakan — `BiayaPerolehan`, `PenyusutanTerakumulasi`, `NilaiBuku` (identitas `assetCost − depreciationAmount = bookValue` terbukti), `MasaManfaat` (bulan), status `Draft`/`Disposed`, dan yang paling penting **`GolonganNama` (`faType.name`) — satu-satunya penggolongan yang bersih dan selalu terisi**. Agregat `RingkasAsetTetap` (total per status/biaya, draft dipisah) juga sudah ada.
- **Akses Accurate = eksklusif Finance.** Hanya tim Finance yang berhak menginput aset ke Accurate; **staff GA tidak boleh menyentuh Accurate sama sekali**. Konsekuensinya, aset yang **belum ada di Accurate adalah tanggung jawab Finance**, bukan GA — dan rekonsiliasi ini justru dirancang untuk **memicu koordinasi lapangan GA ↔ staff Finance inventory**.
- **Akuntansi = domain Accurate.** [[ADR - 0001 Akuntansi via Accurate]]: ERP tidak membangun ledger sendiri; angka aset/penyusutan **resmi** milik Accurate. Nilai buku di ERP hanyalah estimasi operasional GA.
- **Kepemilikan KPI sudah diputuskan.** [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]: `employee_db` satu-satunya pemilik `kpi_score`; nilai otomatis masuk **satu pintu bergerbang** di employee-service, berstatus **DRAFT** (supervisor tetap verifikasi), tidak ada tulis lintas-DB. GA memiliki **24 metrik KPI** hari ini ([[HRIS - Matriks KPI per Departemen]], 2026-08-01). Auto-value KPI **belum merge/deploy**.

Ketegangan intinya: kategori ERP **bebas-ketik** (tak terkontrol) vs golongan Accurate **terkontrol**; dan "kecocokan agregat" mudah dihitung tapi **menyembunyikan kesalahan yang saling menutup** (item hilang + item dobel → total tetap pas), sehingga tak adil bila jadi skor akurasi personal.

## Decision

**Modul Aset diperluas menjadi 3 tab; skor KPI diambil dari ceklis per-item (bukan agregat), dan gap Accurate tidak pernah menghukum GA.**

### 1. Tiga tab di modul Aset

- **Tab A — Kelola Aset** (existing): daftar aset GA, sumber inventory-service `GET /items`.
- **Tab B — Data Accurate**: aset tetap dari Accurate (kolom kebenaran: `GolonganNama`, biaya perolehan, nilai buku, status draft/disposed) via `GET /accounting/fixed-assets` yang **sudah ada**; ditambah **editor tabel pemetaan `kategori-ERP → golongan-Accurate`**. Daftar golongan **diambil live** dari data (`faType`), tidak di-hardcode.
- **Tab C — Cocokkan (ceklis)**: rekonsiliasi **per-item** ERP↔Accurate. Inilah sumber data metrik KPI "akurasi ketepatan stock opname aset".

### 2. Pencocokan = ceklis manual berbantuan (bootstrap kunci bersama)

ERP tak punya `accurate_asset_no` dan nomor Accurate (`APP-042`) tak berpadanan ke ID ERP (`INV-BIP-...`), jadi tak ada kunci bersama untuk join otomatis. Pola: dalam Tab C, item dikelompokkan per golongan (lewat pemetaan Tab B), sistem **menyarankan** pasangan (kemiripan nama/biaya/tanggal), staff **mengonfirmasi centang**. Sekali dikonfirmasi, sistem **menyimpan `accurate_asset_no` pada item ERP** → periode berikutnya kecocokan otomatis. Kunci per-item **terbangun bertahap** tanpa proyek backfill 1:1 di depan. Cocok dengan sifat stock opname yang memang verifikasi manual di lapangan.

### 3. Skor KPI = akurasi per-item; gap Accurate tidak menghukum GA

Skor dihitung **per item yang staff input**, berbobot **kelengkapan + kebenaran** relatif terhadap padanan Accurate-nya (harga, tanggal, golongan, nilai). Karena **GA tidak berhak input ke Accurate**, item ERP yang **belum punya padanan di Accurate dihitung 100%** (bukan salah GA — itu antrean Finance). Skor final hanya menilai irisan yang **punya padanan**. Penyalurannya **wajib lewat jalur [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]**: nilai DRAFT, endpoint internal bergerbang di employee-service, supervisor verifikasi. Menyentuh pemicu `kpi-collector` (ADR-0032 §6) — dievaluasi saat implementasi Fase 2.

### 4. Cakupan wajib tampil berdampingan dengan akurasi (anti-menyesatkan)

Karena "belum ada di Accurate = 100%", akurasi bisa terlihat sempurna padahal cuma sedikit aset yang terekonsiliasi. Maka dashboard **selalu menampilkan dua angka**: **Akurasi** (cocok / aset-yang-punya-padanan → ini yang jadi KPI) **dan Cakupan** (% aset yang punya padanan di Accurate → konteks kejujuran, memicu koordinasi ke Finance). Matrix per-golongan = **rollup** dari ceklis Tab C untuk dashboard kesehatan data level GA.

⚠️ **Amandemen 2026-09-02 — matrix per-golongan → "Ringkasan Cakupan per Jenis".** Karena golongan menjadi vestigial sejak [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]] (praktis hanya satu baris `(tak terpetakan)`), matrix per-golongan diganti ringkasan **2 baris per JENIS**: **Aset Tetap** (Total ERP · Berpadanan · Cakupan **%-target**) dan **Perlengkapan** (Total Accurate · Berpadanan per-unit `accurate_item_no` · Cakupan **INFORMASI**, [[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]]). Cakupan perlengkapan ditandai **info** (bukan target): barang bulk/habis-pakai sengaja tak dipadankan per-unit, jadi % kecil bukan berarti buruk. FE-only, 0 BE baru (pakai `usePerlengkapanStocks` + `usePerlengkapanUnitCount`). Grounded: erp-frontend `reconcile-tab.tsx` (`ringkasanPerJenis`/`terpadanPerlengkapan` di `utils/reconcile.ts`), commit b2411a23.

### 5. Penempatan (hormati batas service)

- **Data Accurate** tetap milik integration-service (`accurate_fixed_assets` + `/accounting/*`).
- **Tabel pemetaan + hasil ceklis (`accurate_asset_no`, status/tanggal rekonsiliasi)** disimpan di **inventory-service** (master & data milik GA). inventory-service **tetap tak memanggil siapa pun** (`InternalURL` kosong dipertahankan).
- **Komposisi Tab C** dilakukan **frontend** (tarik `/items` + `/accounting/fixed-assets` + pemetaan, hitung ceklis/matrix, simpan match balik ke inventory-service) — mengikuti pola client-side yang sudah dipakai export & estimasi penyusutan.
- **Feed KPI** (Fase 2, kode di branch `feat/kpi-akurasi-aset`) = **sumber KPI `akurasi_aset_ga`** di [[Microservices - Employee Service]] (`kpi_sumber_aset.go`, `DaftarkanSumber`) yang menarik `/items` + `/category-mapping` (inventory) + `/accounting/fixed-assets` (integration) — **endpoint yang SUDAH ada** — lalu menghitung akurasi per staff (`created_by`) dengan util murni shared-library, mengisi `AutoValue` **DRAFT** lewat mekanisme [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]. **integration & inventory service + Mongo mereka TAK diubah**; URL modul dibaca dari env (`INVENTORY_MODULE_URL`/`INTEGRATION_MODULE_URL`), **bukan** `InternalURL` (hindari boot-dependency, pola monitoring). Konsisten [[ADR - 0002 Database-per-Service]].

### 6. Dua field baru di sisi ERP (prasyarat minimal)

- **`created_by`** pada `InventoryItem`, diisi dari klaim login saat `CreateInventory` — fondasi atribusi KPI. Backfill lama lewat edit (tanpa migrasi).
- **`accurate_asset_no`** (+ status/tanggal rekonsiliasi) pada item — diisi bertahap oleh ceklis Tab C (butir 2).

**Yang ditolak beserta alasannya:**

- **Membangun reader Aktiva Tetap Accurate baru.** Sudah ada (`accurate_client_aset_tetap.go`, `accurate_fixed_assets`, `/accounting/fixed-assets`). Membangun ulang = membayar dua kali.
- **Menjadikan matrix agregat sebagai skor KPI.** Netting menyembunyikan kesalahan (100% padahal record salah) dan agregat tak beratribusi ke orang. Ceklis per-item menghindari keduanya; matrix hanya untuk presentasi kesehatan data.
- **Menghukum GA atas aset yang belum ada di Accurate.** GA tak berhak input Accurate; itu antrean Finance. Karena itu absent = 100% bagi GA, dengan cakupan ditampilkan agar tetap jujur.
- **Backfill kunci per-item 1:1 di depan.** Mahal & rapuh sebelum manfaat terbukti; ceklis berbantuan menabung `accurate_asset_no` bertahap.
- **Menaruh rekonsiliasi/komputasi di inventory-service sebagai pemanggil Accurate.** Melanggar batas service & membalik "`InternalURL` kosong". FE yang mengomposisi; feed KPI lewat employee-service.
- **Memakai kategori ERP bebas-ketik langsung sebagai bucket.** "Laptop"/"laptop"/"Laptop Gaming" jadi bucket berbeda → agregat sampah. Pemetaan ke golongan terkontrol wajib.

## Desain ringkas (untuk /plan berikutnya)

```
FE modul Aset — 3 tab
 ├─ Tab A Kelola Aset ── inventory GET /items
 ├─ Tab B Data Accurate ── integration GET /accounting/fixed-assets (golongan live)
 │                         + editor pemetaan kategori-ERP → golongan  → simpan @ inventory
 └─ Tab C Cocokkan (ceklis) ── FE tarik kedua sisi + pemetaan
         · saran pasangan (nama/biaya/tanggal) → staff konfirmasi
         · simpan accurate_asset_no + status rekon @ inventory (PATCH item)
         · tampil: Akurasi (KPI) + Cakupan (konteks) + matrix per-golongan (rollup)
                    │
         (Fase 2)  ▼ job baca status rekon → akurasi per-item → endpoint ADR-0032 (DRAFT)
                 employee-service → kpi_score staff GA
```

- **Fase 0** — `created_by` di `InventoryItem` + isi saat create; backfill via edit.
- **Fase 1** — Tab B (Data Accurate + editor pemetaan) & Tab C (ceklis + akurasi/cakupan + matrix). Pencocokan menabung `accurate_asset_no`.
- **Fase 2 (kode ✅, branch `feat/kpi-akurasi-aset` — belum merge/deploy)** — util murni akurasi di shared-library (`ComputeFieldScore`/`PerItemKPIScores`, aturan ERP-only=100), scope baru `individu`, dan sumber `akurasi_aset_ga` di employee-service. Formula `rata_rata` (rata skor per-item) · Target 100 · Arah naik. **`kpi-collector` TIDAK dipisah** (2 konektor keluar < ambang 3, ADR-0032 §6). **Sisa non-kode**: konfigurasi metrik `kpi_template` GA (label + bobot) + env deploy.

## Consequences

**Diterima:**

- Reuse penuh integrasi Aktiva Tetap yang sudah ada (0 kode reader baru); sisi Accurate sudah bersih & teragregasi.
- Skor KPI adil (per orang, tahan netting) & tidak menghukum GA atas gap yang bukan wewenangnya.
- Ceklis berbantuan menabung kunci per-item bertahap — tanpa proyek backfill besar — sekaligus mengoperasionalkan koordinasi GA ↔ Finance.

**Ongkos / catatan:**

- Perlu **master pemetaan `kategori-ERP → golongan-Accurate`** yang dirawat GA; kategori bebas-ketik baru yang belum dipetakan jatuh ke "tak terpetakan" (harus terlihat, bukan disembunyikan).
- `purchase_price` opsional → dimensi nilai pada ceklis/matrix **understated** sampai terisi; kelengkapan didahulukan.
- Nilai buku ERP tetap **estimasi**; rekonsiliasi membandingkan **keberadaan + biaya perolehan + golongan**, tidak memperlakukan nilai buku ERP sebagai kebenaran (hormati [[ADR - 0001 Akuntansi via Accurate]]).
- KPI otomatis tetap **DRAFT + verifikasi supervisor** ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]); ADR ini menambah satu calon sumber, bukan mempercepat rollout auto-value.
- Ketergantungan ceklis pada refresh `accurate_fixed_assets` (cron harian) — data Accurate paling telat 1 hari; cukup untuk stock opname.

**Belum diputuskan (TBD):**

- **Bobot & label** metrik akurasi di `kpi_template` GA (keputusan pemilik metrik/HRGA) — rumus & toleransi sudah tetap di kode (`rata_rata`, harga toleransi 1%, ERP-only=100).
- Toleransi "cocok" untuk selisih tanggal (saat ini: hari yang sama persis).
- Apakah saran pasangan Tab C cukup heuristik sederhana (nama+biaya) atau butuh skor kemiripan lebih kaya.

**Sudah diputuskan sejak ditulis:**

- **`kpi-collector` tidak dipisah** — Fase 2 menambah 2 konektor keluar (inventory + integration), masih di bawah ambang 3 (ADR-0032 §6); komputasi tetap di employee-service.

## Dokumen Terkait

- [[GA - Inventory Management]] · [[Microservices - Inventory Service]] · [[API - Inventory Service]]
- [[Microservices - Integration Service]] · [[API - Integration Service]] · [[External - Accurate]]
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0002 Database-per-Service]]
- [[HRIS - Matriks KPI per Departemen]] · [[HRIS - Otomasi Skor KPI]] · [[RUN - Menambah Metrik KPI Otomatis]] · [[Microservices - Employee Service]]

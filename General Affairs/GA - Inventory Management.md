## Deskripsi

*Sistem inventory General Affairs — pencatatan & kontrol aset/barang perusahaan. **Catatan penting:** nama "Inventory Management" agak menyesatkan; saat ini cakupannya **bukan** mengelola Internal & external inventory sepenuhnya sekaligus, melainkan inventory yang digunakan dari purchase/procurement untuk produksi & penjualan produk tersebut. Arah jangka panjang: GA sebagai pengelola inventory perusahaan (lihat Pertimbangan).*

- **Status**: 🟡 Konsep / Draft
- **Penomoran aset (tag)**: implementasi saat ini `INV-BIP-DDMMYY-NAMA-n` (tanggal dari `purchase_date` WIB, `NAMA` = nama barang **alfanumerik saja** UPPERCASE maks 20 char, `n` = increment) — sudah menyertakan item, sejalan dengan arah yang diinginkan. Kategori & nama barang kini **bebas-ketik** (bukan lagi enum terbatas). ⛔ **Tag = `_id` = segmen path URL** (`PATCH`/`DELETE /item/:id`), jadi `NAMA` **wajib alfanumerik**: generator lama cuma membuang spasi sehingga `/` dari nama "6/128GB" lolos → Fiber `:id` (satu segmen) tak cocok → **"Cannot PATCH"** (barang Xiaomi Redmi 14C, 2026-09-04; diperbaiki `sanitizeItemNameForID`, bip-erp `fix/inv-tag-sanitize`). Karakter `& + . (` juga rapuh & kini ikut disaring. Barang lama ber-tag rusak diperbaiki manual (rename `_id`, skrip migrasi). Detail grounded: [[Microservices - Inventory Service]] · [[API - Inventory Service]].
- **Sudah diimplementasikan (✅) di modul Aset**: daftar + kartu ringkasan (jumlah per status + biaya), pencarian/filter/paginasi client-side, **kolom Karyawan Pemegang** (kosong → "Tersedia di GA"), detail bertab, dan **export Excel**.
- **Serah-terima aset (✅)**: pemegang **opsional** saat buat; alur **Serahkan → menunggu persetujuan SPV → SPV setujui** (tombol Setujui hanya untuk **SPV penaung** departemen penyerah — GA jatuh ke **SPV HR** via `supervised_by`), + **Tarik/Kembalikan**. Bukti serah-terima = **upload dokumen** (mengganti catatan teks).
- **Lokasi & penyusutan (✅)**: aset punya **lokasi** (input manual) & **masa manfaat**; **nilai buku ditampilkan sebagai ESTIMASI** (garis lurus, dihitung frontend) — **bukan** angka pembukuan resmi (akuntansi via Accurate, [[ADR - 0001 Akuntansi via Accurate]]). Estimasi **penyusutan per bulan** (= harga ÷ masa manfaat ÷ 12; tarif garis lurus = 1/masa manfaat, cocok tabel pajak 4th→25% dst) kini ditampilkan juga di **tab Informasi** detail aset (2026-08-22).
- **Riwayat perbaikan + bukti nota (✅ 2026-08-22)**: tiap perbaikan bisa dilampiri **bukti nota** (foto/scan/PDF, boleh >1) — di-upload lewat presigned & disimpan sebagai `documents` pada record perbaikan, tampil di kartu riwayat. Detail: [[Microservices - Inventory Service]].
- **Hapus aset — soft delete (✅, ⚠️ belum merge)**: dari **detail aset**, tombol **Hapus Aset** membuka **dialog konfirmasi** dengan **alasan WAJIB** (tombol Hapus nonaktif sampai alasan terisi; spasi di-trim). Sukses → kembali ke daftar, aset hilang + toast. Penghapusan bersifat **soft**: aset lenyap dari daftar & seluruh turunannya (kartu ringkasan, Opex Marketing, coverage padanan, KPI `akurasi_aset_ga`, penyusutan insentif) namun **datanya tetap tersimpan & bisa dipulihkan tim IT** — riwayat perbaikan + foto tak jadi yatim. **Tanpa tombol restore di UI (v1)**: pemulihan darurat lewat IT. Motivasi: staff GA sering salah input (mis. typo nama yang terlanjur jadi ID/kode barang, yang **tak bisa diedit** karena immutable) lalu minta IT hapus — fitur ini melepas ketergantungan itu tanpa kehilangan data. Detail backend: [[Microservices - Inventory Service]].
- **Rekonsiliasi aset ↔ Accurate untuk KPI (⚠️ Fase 1 ✅; pencocokan & skor DIREVISI 2026-08-22, Fase 2 belum)**: staff GA memasangkan barang ERP dengan Aktiva Tetap Accurate **berbasis NAMA** — mungkin sejak nama Accurate tampil (diambil dari field `description`; sebelumnya semua tampil sebagai golongan "Peralatan Kantor"). Padanan dilakukan di dua layar yang menulis kunci sama (`accurate_asset_no`): **Pengaturan Aset** — **editor padanan langsung barang→aset** (combobox cari **nama + kategori** / **kode + nama**), **menggantikan** editor kategori→golongan yang terbukti keliru; dan tab **Cocokkan** — saran by nama, dengan **padanan lama yang salah** (mis. laptop↔gorden) **ditandai ⚠ + tombol "Ganti ke saran"** (non-destruktif). Skor **Akurasi/Cakupan** menilai kesamaan **data** (harga + tanggal, **tanpa golongan**); aset yang **belum ada di Accurate = 100%** (input Accurate = wewenang Finance, bukan GA) sehingga mendorong koordinasi GA↔Finance. **Feed skor ke KPI (Fase 2) belum jalan.** Keputusan: [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] → [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]]. ⚠️ **2026-09-03**: tab Cocokkan kini punya **pencarian nama barang** (kotak Banner) + **filter status di HEADER kolom "Status"** (ikon filter → checklist MULTI-pilih, kosong = Semua — pola tabel Kelola Aset via `ChecklistFilter variant="header"`, BUKAN laci Banner yang hanya satu-nilai). Empat status: **Cocok / Ada saran / Belum ada padanan / Periksa padanan** (satu sumber `statusCeklis`, dipakai badge & filter). Search+filter **client-side**; skor/cakupan tetap dihitung atas SELURUH aset tetap, hanya daftar yang menyempit. Tab ini juga **mengecualikan barang perlengkapan** (`accurate_item_no`) dari daftar & skornya (lihat butir perlengkapan durable di bawah).
- **Opname & akurasi Perlengkapan via rekonsiliasi Accurate (✅ Implemented — live prod)**: rekonsiliasi GA↔Accurate DIPERLUAS ke barang **kategori Perlengkapan**. Beda dari aset tetap: dicocokkan per-**KUANTITAS** — staff GA meng-input **hitung fisik** saat opname, dibandingkan ke qty Accurate (Accurate = kebenaran; `ga_stok` cuma pembanding), skornya → **KPI** (feed KPI = Fase 2). Muncul di tab **Data Accurate** yang sama lewat **pemilih tipe Aset Tetap / Perlengkapan** (tukar tabel+kolom) — **bukan** tab baru, **bukan** dicampur ke tabel aset tetap. Sync `integration` menangkap **kategori item** Accurate ke `accurate_stocks.category` lewat `item/list.do` (list-stock.do tak kirim `itemCategory`); record hitung fisik disimpan di koleksi `ga_opname` (`GET/POST /api/inventory/perlengkapan-opname`). Kini **per-periode** (`YYYY-MM`, server = bulan berjalan WIB) dengan **unique index `(item_no, periode)`**, pemilih periode + **progres "X/N"** + riwayat bulan lampau read-only. **Masih terbuka**: feed KPI (Fase 2). Keputusan: [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]]. ⚠️ **Amandemen 2026-09-02**: tab FE Perlengkapan berpindah dari **opname** → **EXPLORER PADANAN** (Nomor·Nama·Kuantitas·**Terpasang X/N**·**Total Biaya**, seragam dengan tab Aset Tetap; barang qty-0 disembunyikan) — KPI opname tak pernah live (0 attach di `kpi_template`). Form Hitung Fisik/selisih/akurasi/periode **dibuang dari FE**; koleksi `ga_opname` + endpoint `/perlengkapan-opname` **DIBIARKAN dormant** (data & endpoint utuh, FE stop pakai). Lihat amandemen [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] + [[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]]. ⚠️ **Amandemen 2026-09-02 (Total Biaya)**: kolom **Total Biaya** = **nilai persediaan** Accurate (`balance_total_cost`), disandingkan laporan "Kuantitas Barang" Accurate — diisi task harian `accurate-perlengkapan-cost-refresh` hanya untuk Perlengkapan **qty>0** (biaya cuma ada di `item/detail.do`, mahal per item). **Tanggal beli & nilai buku sengaja TAK ditampilkan**: stok dibeli batch (tak ada satu tanggal beli) dan perlengkapan = akun 1606 tak disusutkan (≠ nilai buku aset tetap). Rincian teknis: [[Microservices - Integration Service]]. ⚠️ **Amandemen 2026-09-03 (lingkup Gudang Utama)**: explorer perlengkapan + Kuantitas + Total Biaya + Cakupan kini **LINGKUP GUDANG GA** ("Gudang Utama"), cocok dengan report Accurate **"Kuantitas Barang per Gudang"** — barang yang stoknya di **gudang lain** (Gudang Sidareja, konsumsi produksi) **tersaring keluar** (dari ±263 agregat → ±223 Gudang Utama). Qty per-gudang diambil dari `item/detail.do.detailWarehouseData` (field `accurate_stocks.gudang_utama_qty`); nama gudang dari env `PERLENGKAPAN_GUDANG`. **Kenapa bukan get-stock.do**: endpoint itu balas qty 0 untuk item di gudang lain **tak bisa dibedakan** dari item Gudang Utama yang kebetulan kosong (cmd/stockprobe 2026-09-03). ⚠️ **Blocklist nama (keputusan GA 2026-09-04)**: 6 item **konsumsi produksi** (`alkohol`, plastik `shrink`) berstok di Gudang Utama & dikategori "Perlengkapan" di Accurate tapi **bukan aset perlengkapan GA** — report Accurate juga mengecualikannya. FE menyaringnya lewat `PERLENGKAPAN_KECUALI_KATA` (substring nama, `use-perlengkapan-opname.ts`); diverifikasi prod: 201 item report cocok PERSIS (Σ qty 1.108 = 1.108). **Berbasis nama = rapuh** (barang baru ber-kata itu ikut terbuang); dicatat sadar.
- **Perlengkapan durable diinput seperti aset tetap + dipadankan (✅ Implemented — [[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]])**: charger/mic/APAR **diinput di Kelola Aset biasa** (campur dengan aset tetap), lalu **dipadankan by-nama** ke item perlengkapan Accurate (`accurate_item_no`) lewat **Pengaturan Aset** — persis editor padanan aset tetap, cuma sisi Accurate = perlengkapan. Jumlah barang terpadan **mengisi otomatis (prefill)** Hitung Fisik opname (bulan berjalan, bisa dikoreksi). Barang massal tetap kuantitas/manual. **Satu-satunya perlakuan khusus**: perlengkapan **tak disusutkan** (akun 1606, tak masuk opex); selebihnya campur. ⚠️ KPI aset tetap (Fase 2) wajib mengecualikannya. ✅ **FE tab Cocokkan kini mengecualikannya (2026-09-03)**: daftar + skor/cakupan/kpiScore aset tetap menyaring item ber-`accurate_item_no` (diskriminator perlengkapan), menutup Consequences [[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]] sisi FE. BE `akurasi_aset_ga` exclusion **tetap Fase 2** (KPI belum attach ke template). Tanpa filter ini, perlengkapan (tak punya `accurate_asset_no`) dihitung 100% ERP-only → kpiScore menggelembung sekaligus coverage turun.
- **Tampilan modul Aset ikut struktur halaman HRIS (✅, ⚠️ belum merge)**: kelima layar (daftar, detail, Data Accurate, Cocokkan, editor pemetaan) memakai komponen bersama `Banner` + `MainTable` + `StatSummary` + `Badge`, menggantikan palet CSS `--as-*` beserta tiruan tabel/pager buatan sendiri. Sekaligus **dwibahasa** ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]), yang sebelumnya belum terpenuhi sama sekali di modul ini. Rincian keputusan & konsekuensinya: [[APP - Web ERP]] §GA.
- Terkait erat dengan [[GA - Procurement System]] (sumber masuknya barang) & [[WH - Management System]] (master data).

## Latar Belakang

GA ingin punya dashboard untuk mengelola aset perusahaan (alat & bahan, ATK, dokumen legal) dalam program paperless yang terintegrasi antar divisi (lihat [[GA - Big Pictures]]).

**GA sebagai "Pengelola" Inventory Perusahaan** — setiap item/objek inventory secara native dimiliki oleh GA; GA dapat menurunkan sebagian item ke departemen lain di mana departemen tersebut akan memelihara item itu sesuai kebutuhan. Modelnya semacam hierarki: GA di puncak, lainnya di bawah.

![[inventory-propergation.png]]

Artinya ada **1 master data** yang disirkulasikan dari GA ke departemen lain sesuai kebutuhan; sebagian departemen (mis. manufaktur) mungkin punya fitur unik terkait cara mereka melihat inventory mereka, dan seterusnya.

## Ruang Lingkup / Fitur

**Scope**
* Pencatatan aset menjadi jelas
* Controlling & monitoring aset
* lokasi barang
* Pencatatan vendor
* Ada informasi SOP pengajuan aset
* Reservasi ruang meeting & peminjaman aset (lihat [[GA - Asset Loan & Room Booking]])

**Breakdown fitur**
- **Dashboard** — ikhtisar yang baik untuk pelaporan ke stakeholder; ringkasan detail purchases, sales, stok, dan profit; volume aktivitas / perubahan stok
- **Purchases** *(mengapa fitur ini ada di sini?)* — purchase/procurement normal untuk produk, dengan detail vendor/supplier. GA punya dana **petty cash** untuk pengeluaran yang dikonsumsi dalam satu bulan (mis. perlengkapan kantor, peralatan kebersihan, atau request barang ≤ Rp2 juta/bulan). Bila demikian, **Finance tetap satu-satunya pemilik sistem purchasing**; GA dapat melakukan request dan melihat entri procurement mereka yang disetujui.
- **Sales** *(mengapa fitur ini ada di sini?)* — sales normal untuk produk, tetapi tanpa info ke mana produk dijual. Disepakati lebih baik **dipindah ke modulnya sendiri** (mis. ke Finance System).
- **[[CORE - OCR Document Service|OCR Document]]** (shared service) — dokumen fisik di-scan jadi gambar lalu di-upload; OCR membaca dokumen untuk kebutuhan lain (mis. pencarian judul dokumen, isi dokumen, nomor tertentu di dalam dokumen).

**Master data terkait**
- **Warehouse Master Data** — mengelola hal-hal apa yang disimpan di warehouse saat ini, dengan Stock Keeping Unit (SKU) dan barcode untuk menciptakan alur sistem yang lebih baik.
- **Internal Inventory** *(belum ada / belum disebutkan per 10/7/25 pada [berkas dokumen Bharata di Google Drive](https://drive.google.com/drive/folders/1gKly790zuff8roX3kLQq1TVE02jT7drK))* — akan melacak semua aset perusahaan & menjadi dependency untuk sistem mendatang (mis. perbaikan). Bisa menjadi **child** dari GA - Inventory Management untuk semua barang ber-tag internal, lalu ke depannya diturunkan ke tiap sistem (mis. IT, HR) untuk mengelola internal inventory mereka sendiri. Fitur: Dashboard; pembuatan & penandaan aset individual (sangat menyerupai salah satu fitur [[WH - Management System]]); penugasan aset ke karyawan.

## Alur

berikut alur sebuah barang menjadi aset perusahaan dari awal hingga akhir.
1. User mengajukan barang dengan mengisi form disertai tanda tangan SPV departement ybs. ([[Form Permintaan Barang GA.pdf]])
2. Form ini diserahkan ke GA dan dilakukan nego dengan mencarikan alternatif lain. minimal 3 pilihan barang yang sama dengan harga yang berbeda
3. GA dan user memilih barang sesuai dengan vendor yang dipilih
4. GA melakukan approval yang diwakili oleh Spv dan meneruskan proses
5. GA menentukan pembayaran dengan ketentuan
	* apabila harga barang kurang dari Rp. 3.000.000, maka tidak memerlukan tanda tangan Direktur
	* apabila harga barang lebih dari Rp. 3.000.000, maka memerlukan persetujuan Direktur melalui sekretariat
6. apabila sudah dilakukan approval di step 5 diatas, maka GA melanjutkan proses dengan melakukan PO
7. Barang akan dikirim
8. Setelah barang sampai, GA melakukan pencatatan dan melakukan penomoran (Jenis-Ruangan-Bulan-Tahun) dan menyerahkan barang ke User.
9. Form penerimaan barang diisi sebagai bentuk pencatatan.

## Hasil Observasi

Tanggal 13 Januari 2026
#### kendala yang dialami tim GA:
1. Ruangan aset yang belum ada. ruangan atau gudang aset & barang tidak terpakai belum ada. sehingga sementara ini barang-barang tersebut diletakan seadanya
2. Barang material diletakan dilokasi yang seadanya (khusus jika ada pembangunan)
3. Pencatatan barang yang rusak

#### Kategori barang
1. Barang Office
2. Produksi & warehouse
3. Aset building

#### Sifat barang
1. Konsumsi (Kopi, gula) (fixed cost)
2. Aset (Sesuai kebutuhan)

## Pertimbangan & Belum Diputuskan (TBD)

- **Gabung dengan internal inventory?** Keduanya kemungkinan punya banyak fitur sama, jadi bisa ditaruh di sini + tag tambahan untuk item yang dipakai internal. Mungkin kurang diinginkan jika internal inventory tidak dikelola secara native oleh GA. → **Disimpulkan pertimbangan ini valid** & dapat dipakai pada situasi saat ini karena diturunkan/dinaikkan rapi berdasarkan tingkat kepentingan & level saat ini; pengembangan dapat dilanjutkan.
- Jenis inventory & detail apa yang diinginkan? (mis. bahan baku produksi minim info; komputer banyak info termasuk SN). Bagaimana cara menyimpannya — berbasis barcode dengan SKU pada lokasi keberadaannya? Bagaimana diturunkan ke departemen?
- [ ] (Detail tertunda) Database Internal Inventory sepertinya bisa digabung dengan Warehouse Master Data dengan flag eksplisit untuk barang internal inventory.
- **Masalah yang mungkin muncul dari departemen lain:**
	- **Finance** — Purchase/procurement order diperlukan untuk memvalidasi entri; Sales order diperlukan untuk memvalidasi entri.
	- **Warehouse** — Dokumen tambahan untuk memvalidasi bahwa produk dipindahkan masuk/keluar dari warehouse.

## Kebutuhan

- [ ] Warehouse master data (lihat referensi)
- [ ] Data purchase dari finance
- [ ] Data sales dari finance

## Referensi

Sistem yang sudah ada:
1. Inventa

## Dependensi / Dokumen Terkait

- [[WH - Management System]]
- [[GA - Procurement System]] · [[CORE - OCR Document Service]]
- [[GA - Asset Loan & Room Booking]] — alur pinjam ruang/aset
- [[GA - Big Pictures]]

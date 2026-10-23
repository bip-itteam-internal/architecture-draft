> **Status**: 🟢 **Diterima, 2026-10-13, oleh wirkancil (Pemutus Pembelian Raw Material/Barang Umum)** lewat sesi desain saat uji Barang Umum di produksi. **Belum ada kode.**

## Untuk Manajemen

**Apa yang diputuskan.**
1. **Stok perlengkapan yang dipakai untuk memutuskan "barang ready" adalah stok GA di ERP**, bukan qty Accurate. Stok ini diisi GA lewat stock opname, bertambah saat barang pembelian diterima, berkurang saat barang diserahkan, dan menahan cadangan permintaan karyawan.
2. **Accurate tetap acuan akuntansi.** Supaya angkanya ikut bergerak, ERP **otomatis mengirim Penyesuaian Persediaan** ke Accurate saat GA menyerahkan barang (barang keluar = biaya pemakaian) dan saat ada stock opname/penyesuaian di ERP. Barang masuk sudah sampai ke Accurate lewat faktur pembelian.
3. **Halaman baru "Stok Perlengkapan"** di menu GA: melihat stok, menambah barang habis pakai ke katalog, stock opname/penyesuaian beralasan dengan riwayat, dan mengubah jenis barang (aset ↔ perlengkapan).

**Siapa yang terdampak.** Staf GA (stock opname, penyesuaian), Finance (Penyesuaian Persediaan otomatis di Accurate; akun beban dan departemen pemakai ditetapkan bersama Finance), karyawan pemohon barang (permintaan tak lagi ditolak karena stok tak tercatat).

**Kenapa perlu ditulis.** Diukur di produksi 2026-10-13: stok GA kosong, 1 dari 144 barang katalog berjenis perlengkapan, dan tidak ada layar maupun endpoint untuk mengisi stok. Akibatnya setiap permintaan barang terbaca "tidak ready" dan berakhir jadi pembelian walau barangnya ada di rak. Sementara itu [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] menyatakan Accurate sumber kebenaran jumlah perlengkapan dan "bukan sistem stok gudang baru", padahal kode permintaan dan cek stok sudah memakai stok GA sebagai stok operasional.

**Apa yang tidak dijanjikan.**
- **Akun beban dan departemen** Penyesuaian Persediaan belum ditetapkan; paket pengirimannya menunggu keputusan Finance.
- **Rekonsiliasi ERP vs Accurate** ([[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]]) tetap ada sebagai pemeriksa selisih, bukan sumber angka "ready".
- **Perlengkapan awet per unit** ([[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]]) tidak berubah: unitnya tetap dihitung dari unit menganggur di daftar Aset.

**Perkiraan besaran kerja.** Sedang sampai besar (estimasi): backend inventory (stok, penyesuaian, riwayat, katalog), layar Stok Perlengkapan, dan satu paket pengiriman Penyesuaian Persediaan ke Accurate.

## Deskripsi

*Stok GA (`ga_stok`) di ERP menjadi stok operasional perlengkapan untuk permintaan dan cek stok; Accurate tetap acuan akuntansi dan menerima Penyesuaian Persediaan otomatis untuk barang keluar dan penyesuaian. Mengubah Decision 3 dan kalimat "bukan sistem stok gudang baru" di [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]].*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Spec**: bip-erp `docs/superpowers/specs/2026-10-13-permintaan-ga-menunggu-stok-design.md` (PR bip-itteam-internal/bip-erp#3033), Keputusan 11–13
- **Issue**: induk bip-itteam-internal/bip-erp#2616; Stok Perlengkapan bip-itteam-internal/bip-erp#3034 + bip-itteam-internal/erp-frontend#2369
- **Tanggal**: 2026-10-13

## Context

Diukur di kode (`origin/main` 2026-10-13) dan produksi (baca saja):

- **Stok GA sudah berperilaku sebagai stok operasional di kode**: bertambah di penerimaan barang pembelian (`TambahStokFisik`, `services/inventory/ga_stok_repo.go:167`), berkurang saat diserahkan (`/internal/ga-stok/kurangi`), dan menahan cadangan permintaan (`filterCadangkan`). Cek stok Barang Umum dan Permintaan Barang GA membaca `tersedia = fisik − dicadangkan` (`permintaan_ketersediaan.go:143`). Yang tidak ada hanya **pengisian awal dan penyesuaian**.
- **Produksi**: `ga_stok` 0 baris; katalog GA 144 barang (143 aset, 1 perlengkapan); 871 unit aset berstatus Tersedia tetapi hanya 1 yang tidak dipegang siapa pun.
- **Accurate**: faktur pembelian Barang Umum mencatat baris barang ke gudang "Gudang GA", jadi barang masuk menambah persediaan Accurate. Penyerahan dan opname di ERP tidak mengirim apa pun, jadi Accurate tidak berkurang.
- **Pola Penyesuaian Persediaan ke Accurate sudah ada** untuk barang sampel Marketing (`services/integration`, akun penampung Penyesuaian Persediaan sampel).
- Backend opname [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] (`/perlengkapan-opname`, koleksi `ga_opname`) dalam keadaan dorman sejak amandemen 2026-09-02.

## Decision

1. **`ga_stok` = stok operasional perlengkapan** untuk menentukan "ready", mencadangkan, dan menyerahkan. Sumber angkanya: stock opname/penyesuaian GA, penerimaan barang pembelian, dan penyerahan. Semua perubahan lewat satu fungsi yang mencatat riwayat.
2. **Halaman Stok Perlengkapan** (menu GA): daftar stok, tambah barang perlengkapan ke katalog, penyesuaian `OPNAME`/`TAMBAH`/`KURANGI` beralasan, ubah jenis barang. Izin `ga.view` untuk melihat, `ga.work` untuk mengubah.
3. **Penyesuaian Persediaan otomatis ke Accurate** saat barang diserahkan dan saat penyesuaian/opname di ERP, dengan pola barang sampel Marketing. Akun beban dan departemen pemakai: **TBD bersama Finance**; paketnya tidak dikerjakan sebelum itu tertulis.
4. **Accurate tetap acuan akuntansi** dan rekonsiliasi ERP vs Accurate tetap berjalan sebagai pemeriksa selisih.
5. `ga_opname` dan `/perlengkapan-opname` dibiarkan dorman; stock opname baru menulis `ga_stok` lewat penyesuaian `OPNAME`, tidak ke `ga_opname`.

## Consequences

- Satu angka "ready" untuk permintaan dan cek stok, dan GA bisa memperbaikinya sendiri lewat opname.
- Selama paket Penyesuaian Persediaan belum jalan, Accurate tetap lebih tinggi dari ERP untuk barang yang sudah diserahkan; selisihnya terlihat di rekonsiliasi.
- Perubahan jenis barang aset ↔ perlengkapan dijaga: tidak boleh bila masih ada unit aset (ke perlengkapan) atau stok/cadangan (ke aset).

## Alternatif yang ditolak

- **Qty Accurate sebagai acuan "ready"** (tersedia = qty Accurate − cadangan ERP): Accurate tidak menyimpan cadangan permintaan, angkanya hanya bergerak bila Finance mencatat, dan barang katalog harus dipadankan ke item Accurate lebih dulu.
- **Stok GA dan Accurate dibiarkan terpisah, cukup rekonsiliasi**: biaya pemakaian tak pernah tercatat di Accurate dan selisihnya terus membesar.

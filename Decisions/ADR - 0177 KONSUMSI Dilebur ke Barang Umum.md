# ADR - 0177 KONSUMSI Dilebur ke Barang Umum

> **Status**: 🟢 **Diterima, 2026-10-13, oleh wirkancil (Pemutus Pembelian Raw Material/Barang Umum)** sebagai Keputusan 8 spec permintaan GA (`docs/superpowers/specs/2026-10-13-permintaan-ga-menunggu-stok-design.md` di bip-erp, PR `bip-erp#3033`, merged). **Implementasi**: backend `bip-erp#3046` dan layar `erp-frontend#2373`, keduanya **belum merged** (diukur 2026-10-13). Menggantikan [[ADR - 0154 KONSUMSI Dibelikan Procurement seperti Raw Material, Bukan Permintaan Uang]].

%% Vault ini PUBLIK. Nama orang dan employee_id tidak ditulis; yang disebut hanya angka agregat, departemen, dan posisi. Pemutus disebut dengan login GitHub, seperti ADR lain. %%

## Untuk Manajemen

**Yang diputuskan.** Jenis pengajuan **Konsumsi tidak lagi berdiri sendiri**: barang konsumsi (pantry, galon, jamuan) diajukan sebagai **Barang Umum**. Satu jenis, satu alur: cek stok GA dulu, kekurangannya dibeli Procurement. Pembayar Barang Umum tetap bisa dipilih.

**Kenapa.** Konsumsi dan Barang Umum hanya berbeda tiga hal (cek stok GA, kapan atasan disisipkan, dan pembayar selalu PT Bharata); katalog, Procurement, metode bayar, barang tiba, QC GA, terima GA, dan faktur sudah sama. Dua jenis yang hampir sama membuat pengaju harus memilih tanpa tahu bedanya. Produksi 2026-10-13: **0 dokumen KONSUMSI**, jadi tak ada dokumen berjalan yang terdampak.

**Yang tidak berubah.** Dokumen KONSUMSI lama tetap terbaca, tetap berjalan, tetap dibayar PT Bharata, dan tetap bisa diajukan ulang.

## Deskripsi

*Tipe pengajuan `KONSUMSI` keluar dari daftar tipe yang bisa diajukan baru; barang konsumsi diajukan lewat `UMUM`. Tipe itu tetap dikenal sistem untuk dokumen lama.*

- **Tanggal**: 2026-10-13
- **Status**: lihat blockquote di baris pertama dokumen ini
- **Menggantikan**: [[ADR - 0154 KONSUMSI Dibelikan Procurement seperti Raw Material, Bukan Permintaan Uang]] seluruhnya untuk pengajuan BARU, dan keputusan 16 spec pembelian 2026-10-05. [[ADR - 0090 KONSUMSI Eskalasi ke Direktur di Ambang Berbagi, Bukan Kebal]] ikut tak berlaku untuk pengajuan baru.
- **Konteks lebih luas**: Keputusan 12 spec yang sama: konsumsi = perlengkapan (habis pakai) di gudang GA, tanpa halaman khusus; lihat [[ADR - 0175 Stok GA di ERP Jadi Stok Operasional, Barang Keluar dan Penyesuaian Dikirim ke Accurate]].

## Context

- Data produksi 2026-10-13 (dikutip spec): 0 dokumen `pengajuan_barang` ber-tipe KONSUMSI, UMUM, maupun RAWMATERIAL.
- Mekanisme sebelum perubahan (`bip-erp` `origin/main`, 2026-10-13): `TipeBarangDikenal` memuat KONSUMSI (`pengajuan_barang_jenjang.go`); `departemenPerTipe` memberi KONSUMSI ke grup HRGA (`pengajuan_barang_gate.go`); `TipeSelaluDibayarPTBharata` = RAWMATERIAL dan KONSUMSI (`pengajuan_barang_pt_bharata.go`); `GET /pengajuan-barang/tipe-boleh` menawarkan KONSUMSI ke HRGA dan super-akses IT.

## Decision

1. **Pembuatan baru ditolak.** `POST /pengajuan-barang` ber-tipe `KONSUMSI` dibalas `400 {"error": "tipe Konsumsi sudah dilebur ke Barang Umum"}`, sebelum gerbang departemen dan berlaku juga bagi super-akses.
2. **Tidak ditawarkan.** `GET /pengajuan-barang/tipe-boleh` tidak memuat KONSUMSI di cabang mana pun, termasuk super-akses IT dan kunci `selalu_pt_bharata`. Layar pembuatan mengikuti daftar itu tanpa salinan, jadi kartu Konsumsi hilang sendiri; keterangan Barang Umum menyebut "termasuk barang konsumsi".
3. **Tetap dikenal untuk dokumen lama.** KONSUMSI tetap di `TipeBarangDikenal` (lolos `ValidasiTipeBarang`) dan tetap selalu PT Bharata saat submit; jalur ajukan ulang tidak membaca gerbang pembuatan. KONSUMSI keluar dari `departemenPerTipe`.
4. **Satu tempat.** Daftar tipe yang dilebur hidup di `tipeDilebur` (`pengajuan_barang_jenjang.go`), dibaca `TipeBisaDiajukanBaru` dan `PesanTipeDilebur`. Tipe lain yang kelak dilebur cukup ditambahkan di sana.

## Consequences

- **Urutan deploy**: procurement (`bip-erp#3046`) lebih dulu, lalu layar (`erp-frontend#2373`). Sebelum procurement naik, Konsumsi tetap tampil sebagai pilihan (perilaku lama, aman).
- Barang konsumsi yang dulu "selalu PT Bharata" kini ikut aturan pembayar Barang Umum (bisa dipilih). Bila Finance ingin konsumsi tetap selalu PT Bharata, itu keputusan baru: TBD.
- Dok yang menyebut KONSUMSI sebagai tipe aktif ([[Microservices - Procurement Service]], [[API - Procurement Service]]) diperbarui bersamaan dengan ADR ini.

## Dokumen Terkait

- [[ADR - 0154 KONSUMSI Dibelikan Procurement seperti Raw Material, Bukan Permintaan Uang]] · [[ADR - 0090 KONSUMSI Eskalasi ke Direktur di Ambang Berbagi, Bukan Kebal]] · [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]]
- [[ADR - 0175 Stok GA di ERP Jadi Stok Operasional, Barang Keluar dan Penyesuaian Dikirim ke Accurate]]
- [[Microservices - Procurement Service]] · [[API - Procurement Service]] · [[GA - Inventory Management]]

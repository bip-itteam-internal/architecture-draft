> Papan kerja penataan fondasi sistem Manufaktur (produksi, PPIC, gudang bahan dan barang jadi, Quality), dibuat 2026-10-13. Temuan dan keputusan terbuka ada di [[Manufacture - Kajian Fondasi Sistem]]; peta rantai lintas modul di [[REF - Rantai Pengajuan Lintas Modul]]. Berkas ini berubah tiap butir bergerak; dok di atas tidak.

**Issue induk:** bip-itteam-internal/bip-erp#3068 `[Fondasi Manufaktur] Penataan produksi, gudang, dan QC` (Project #15, label `fondasi-manufaktur` di semua issue terkait). Issue yang sudah punya induk lain (#2595 dan #3038 di bawah #2616; #2251 dengan sub-issue-nya) tidak dipindah, hanya ditautkan lewat komentar penghubung. Duplikat bip-erp#2357 ditutup, keputusan K-7 dibahas di #2189.

# Aturan pakai papan ini

1. **Sebelum membuat issue, kode, atau data master baru, cari butirnya di tabel ini.** Bila sudah ada issue, kerjakan di issue itu; jangan membuat yang baru.
2. **Satu butir = satu kode (M-nn).** Sebut kodenya di judul brief, branch, atau PR supaya bisa dilacak balik.
3. **Butir bertanda Menunggu tidak boleh dikerjakan** sampai keputusannya tertulis di ADR berstatus Diterima.
4. **Data master** (barang, produk, gudang) tidak dibuat di tempat baru sampai [[ADR - 0136 Pemilik Master Barang dan Master Gudang]] diputuskan.
5. **Cek kerja paralel**: `/papan-sesi` dan assignee issue sebelum mulai.
6. Status bergerak (open, merged, deployed) diukur ulang dari GitHub, bukan disalin dari tabel ini. Kolom Status di sini hanya: Siap / Menunggu keputusan / Berjalan / Selesai.

# Keputusan yang ditunggu

| Kode | Keputusan | Pemutus | Preseden / dok |
|---|---|---|---|
| K-1 | Pemilik angka stok pabrik (ERP lalu dikirim ke Accurate, atau Accurate) dan urutan validasi opname | Finance Supervisor | [[ADR - 0175 Stok GA di ERP Jadi Stok Operasional, Barang Keluar dan Penyesuaian Dikirim ke Accurate]] untuk GA |
| K-2 | Zona WIP: kapan stok bahan berkurang, kapan pemakaian final dihitung | SPV Manufacture + Supervisor Quality | kajian, Temuan 3 |
| K-3 | Satu keputusan rilis oleh Penanggung Jawab Teknis; pilihan nasib barang yang ditolak | Supervisor Quality + PJT | kajian, Temuan 6-7 |
| K-4 | Status bahan masuk (Karantina, Lulus, Reject, Ditolak) | Leader Warehouse + Supervisor Quality | kajian, Temuan 3 |
| K-5 | Format cetak yang diterima BPOM (kartu stok, Batch Record) | Supervisor Quality | kajian |
| K-6 | Pemilik perhitungan HPP per batch | Finance Supervisor | kajian |
| K-7 | Pemilik master barang dan gudang | TBD (IT + manajemen) | [[ADR - 0136 Pemilik Master Barang dan Master Gudang]] |
| K-8 | COA keluar: format per lini (Pangan, OT, Kosmetik), per batch atau per Surat Jalan, penanda tangan | Supervisor Quality + PJT | kajian, Temuan 5 |
| K-9 | Gerbang ketersediaan bahan; siapa menyetujui bahan pengganti | SPV Manufacture + PJT | kajian, Temuan 7 |
| K-10 | MOQ dan aturan ubah Production Order | SPV Manufacture + SPV Marketing | kajian, Temuan 3 |
| K-11 | Selisih RM: fitur sendiri (#2252, FE #1849) atau bagian dari satu jalur penyesuaian stok | SPV Manufacture | konflik terbuka, lihat M-12 |

# Daftar butir

Repo: **BE** = bip-erp, **FE** = erp-frontend. Status per 2026-10-13.

## Fase 1: adopsi yang sudah ada (tak menunggu keputusan)

| Kode | Butir | Issue yang ada | Butuh | Status |
|---|---|---|---|---|
| M-01 | Cek dan beri akses menu Manufaktur/Quality ke posisi yang benar (paket hak per jabatan) | BE #2434 (tolak setuju CAPA karena nama role) | - | Siap |
| M-02 | Uji coba Batch Record pada 1-2 batch nyata, paralel dengan kertas | - | M-01 | Siap |
| M-03 | Tambah bagian spesifikasi produk di Batch Record (dasar COA) | BE #3077, FE #2413 | - | PR terbuka 2026-10-14 (BE #3084, FE #2417); deploy BE dulu, QA RND login ulang |
| M-04 | Dashboard jembatan dari spreadsheet PPIC untuk SPV Manufacture | - | - | Siap |
| M-05 | Sinkronkan [[Microservices - Manufacture Service]] dan [[API - Manufacture Service]] dengan kode (batch record, cycle count, lot, K3/GMP, /kpi/*) | - | - | Siap |
| M-06 | Rapikan data jabatan di HRIS (posisi yang menjalankan tugas PPIC) | - | konfirmasi SPV | Siap |

## Fase 2: rapikan fondasi

| Kode | Butir | Issue yang ada | Butuh | Status |
|---|---|---|---|---|
| M-10 | Satu Batch Record sebagai catatan produksi; buang jalur produksi ganda; penyimpangan dihitung sistem | BE #2195 | K-2 | Menunggu keputusan |
| M-11 | Satu keputusan rilis; FG berstatus karantina sampai rilis | BE #2198, #2248 | K-3 | Menunggu keputusan |
| M-12 | Satu jalur penyesuaian stok (opname, selisih) dengan persetujuan berjenjang | FE #1868, BE #2252, FE #1849; pola push dari BE #3038 | K-1, K-11 | Menunggu keputusan |
| M-13 | Satu gerbang QC bahan masuk dengan status karantina | BE #2190, #2250, #2249 | K-4 | Menunggu keputusan |
| M-14 | PO bahan hanya di Procurement; PPIC membaca PO; tahap PPIC di pengajuan barang | BE #2197, #2595, #2616 | - | Siap (koordinasi pemilik #2616) |
| M-15 | Satu rute Production Order / MO Marketing | - | K-10 | Menunggu keputusan |
| M-16 | Menu Manufaktur dan Quality ke model [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] + panduan per menu | - | - | Siap |
| M-17 | Kartu stok per lot, cetak | FE #1867 | K-5 | Menunggu keputusan |
| M-18 | Mutasi antar gudang terkait status FG | FE #1869 | - | Siap |

## Fase 3: fitur baru

| Kode | Butir | Issue yang ada | Butuh | Status |
|---|---|---|---|---|
| M-20 | Jadwal produksi + gerbang ketersediaan bahan + permintaan bahan + serah ke WIP | (sebagian BE #2195) | K-2, K-9 | Menunggu keputusan |
| M-21 | Surat Jalan + COA keluar | - | K-8, M-03 | Menunggu keputusan |
| M-22 | Production Order dengan MOQ dan satu kali ubah | - | K-10 | Menunggu keputusan |
| M-23 | Safety stock, ROP, MRP dengan bahan sedang dipesan | - | M-14 | Siap setelah M-14 |
| M-24 | Retur ke pemasok dari bahan ditolak QC | - | K-4 | Menunggu keputusan |
| M-25 | Laporan mutasi persediaan dan fisik vs Accurate | - | K-1 | Menunggu keputusan |
| M-26 | HPP per batch | BE #2505 (keamanan biaya variabel) | K-6 | Menunggu keputusan |
| M-27 | Dashboard KPI Quality | BE #2246 | M-11, M-13 | Menunggu |
| M-28 | CAPA dari komplain dan penyimpangan | BE #2251, #2191, #2247; #2235 (Marketing) | - | Siap |
| M-29 | Pengawasan proses produksi | FE #1848 | M-10 | Menunggu |

## Fase 4: berikutnya

| Kode | Butir | Issue yang ada | Status |
|---|---|---|---|
| M-40 | Kondisi mesin, inspeksi, laporan kerusakan | - | Belum dijadwalkan |
| M-41 | Lini Pangan | - | Belum dijadwalkan |
| M-42 | Inspeksi diri / audit internal, change control, pengendalian dokumen | - | Belum dijadwalkan |

## Di luar cakupan, jangan diubah dari papan ini

- Scan retur marketplace dan pengamannya (BE #2796, FE #1896, [[ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu, Lalu Konfirmasi Massal Hanya untuk Baris Cocok]]): satu-satunya alur manufaktur yang aktif dipakai.
- Stok gudang packing dan order marketplace (BE #2194, #2302, #2304, #2305).

# ANALISA - Proyeksi Forecast Kas Mingguan Diatur per Minggu

> 🟢 ADR-nya **Diterima** 2026-10-09 oleh Azzerith. Issue sudah dibuat (lihat §Urutan). Keadaan 2026-10-09 (bergerak, ukur ulang sebelum dipakai): bip-erp#2865 PR terbuka (bip-erp #2872); pekerjaan BE dan FE fitur ini belum mulai.

- **ADR**: [[ADR - 0161 Proyeksi Forecast Kas Mingguan Diatur Porsinya per Minggu oleh Cost Control, Jumlah Sebulan Tetap RAPB]]
- **Dok domain**: [[Finance - Serapan Anggaran dan Cost Control]] § Proyeksi Mingguan Diatur per Minggu · [[Finance - Rancangan Finance Service]] · [[API - Integration Service]]
- **Pemutus**: `Azzerith`
- **Dibuat**: 2026-10-09, hasil `/analisa-kebutuhan`
- **Ukuran**: **Sedang**. Dua repo (`bip-erp`, `erp-frontend`), masing-masing satu PR. `my-bharata` tidak tersentuh: tidak ada pembaca endpoint mingguan di sana yang ditemukan, dan repo itu tidak diperiksa lebih jauh.

## Kebutuhan

Yang diminta: proyeksi Forecast Mingguan bisa diedit manual. Kebutuhannya: pengeluaran kas tidak merata tiap minggu, jadi porsi proyeksi tiap minggu harus mengikuti jadwal bayar, tanpa mengubah total anggaran bulan itu.

## Yang diputuskan pemohon (2026-10-09)

1. Yang diketik total per minggu; jumlah sebulan tetap sama dengan RAPB.
2. Minggu terkunci saat mulai dan sesudah lewat.
3. Tiap minggu yang belum mulai paling banyak diubah 2 kali.
4. Riwayat pengeditan di bawah tabel: siapa, kapan, apa yang berubah.
5. Bentuk simpan: porsi per minggu (Opsi 1), supaya tabel rincian per akun ikut dan RAPB tetap satu sumber.
6. Tetap dibangun walau skor KPI akhir bulan tidak berubah.
7. Unggah ulang RAPB di tengah bulan: porsi diterapkan ke anggaran baru untuk semua minggu, termasuk yang terkunci.
8. Bulan mendatang boleh diatur sebelum bulannya mulai.
9. Tidak ada tombol kembalikan ke bawaan.

## Urutan

| Urutan | Task | Repo | Menunggu |
|---|---|---|---|
| 0 | bip-erp#2865: minggu yang belum selesai tidak dihitung ke akurasi dan KPI | `bip-erp` | Pemutus menegaskan rinciannya |
| Induk | [bip-erp#2877](https://github.com/bip-itteam-internal/bip-erp/issues/2877) (tanpa PR sendiri) | `bip-erp` | |
| 1 | [bip-erp#2878](https://github.com/bip-itteam-internal/bip-erp/issues/2878) [BE] Simpan porsi mingguan, kunci, batas ubah, riwayat | `bip-erp` | #2865 merged (berkas yang sama) |
| 2 | [erp-frontend#2232](https://github.com/bip-itteam-internal/erp-frontend/issues/2232) [FE] Form atur proyeksi dan tabel riwayat | `erp-frontend` | erp-frontend#2230 merged; deploy sesudah task 1 |

Deploy backend sebelum frontend.

### Task 1, [BE]

Yang harus benar:

- Simpan menerima total rupiah per minggu untuk satu periode; ditolak bila jumlahnya tidak sama dengan anggaran kas-keluar periode itu, bila menyentuh minggu yang sudah mulai (WIB), atau bila sebuah minggu yang berubah sudah 2 kali diubah. Pesan penolakan menyebut sebabnya dan minggunya.
- Yang tersimpan porsi per minggu, satu set per (tahun, bulan). Laporan mingguan dan endpoint ringkas KPI memakai porsi itu bila ada, pembagian menurut jumlah hari bila tidak ada.
- Total proyeksi bulan sebelum dan sesudah diatur **sama persis** (test kontrol), termasuk sisa pembulatan.
- Riwayat hanya-tambah, memuat pengubah, waktu, dan per minggu sebelum → sesudah; simpan gagal bila riwayat gagal tercatat. Hitungan "sudah berapa kali diubah" diturunkan dari riwayat.
- Respons baca memuat per minggu: terkunci atau tidak, dan sisa kesempatan ubah. Layar tidak menghitungnya sendiri.
- Rute tulis digerbang `finance.anggaran.kelola` di pendaftaran rute, rute baca riwayat digerbang izin baca; keduanya masuk daftar pemindai gerbang yang sudah ada.
- Penentu "minggu sudah mulai" fungsi murni berargumen waktu acuan; diuji di batas hari WIB. Minimal satu test lewat `app.Test` untuk tiap jalur penolakan.
- Teks alat asisten yang menyebut proyeksi dibagi menurut jumlah hari diperbarui.

### Task 2, [FE]

Yang harus benar:

- Pemegang izin kelola melihat aksi **Atur proyeksi**; pembaca biasa tidak. Minggu terkunci tampil tidak bisa diubah, dengan sisa kesempatan ubah per minggu terlihat.
- Selisih terhadap anggaran bulan terlihat selagi mengetik, dan Simpan nonaktif selama jumlahnya belum sama. Penolakan backend ditampilkan apa adanya.
- Tabel riwayat di bawah tabel forecast: pengubah, waktu, minggu, sebelum → sesudah; keadaan memuat, kosong, dan galat dibedakan.
- Kalimat "tidak ada yang diisi di tab ini" diganti. Semua teks lewat i18n (id dan en); uang dan waktu diformat sadar-bahasa di render.
- Layar tidak menghitung kunci maupun batas ubah sendiri.

## Yang sengaja tidak dikerjakan

- Pengaturan per akun per minggu.
- Mengubah rumus KPI Cost Control #4 (total sebulan) menjadi rata-rata akurasi mingguan.
- Persetujuan atasan per perubahan.
- Pemicu manual penarikan realisasi mingguan.

## Yang masih terbuka

Tinggal asal nama pengubah di riwayat (disalin saat simpan atau diambil saat tampil), diserahkan ke pelaksana backend. Kontrak endpoint ada di badan kedua sub-issue, identik.

## Yang perlu disampaikan ke manajemen

Fitur ini membuat angka per minggu lebih tepat, tetapi **tidak mengubah skor KPI akhir bulan**, karena KPI dihitung dari total sebulan dan total itu tetap.

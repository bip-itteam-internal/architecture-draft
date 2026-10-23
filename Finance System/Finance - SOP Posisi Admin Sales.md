## Deskripsi

*Salinan **1 dokumen SOP** posisi **Admin Sales** (unit Finance) PT Bharata Internasional Pharmaceutical, diambil dari kumpulan "SOP BHARATA 2026". Isinya proses kerja yang dijalankan orang, disalin apa adanya dari dokumen sumber, bukan gambaran perilaku sistem ERP.*

- **Status**: 🟡 **Rekaman SOP (proses bisnis, non-kode).** Kepatuhan sistem ERP terhadap SOP ini belum dipetakan (TBD).
- **Sumber**: `SOP BHARATA 2026/FINANCE/ADMIN SALES` (ekspor Google Drive 2026-10-10, di luar repo). Dokumen sumber yang menang bila salinan ini berbeda.
- **Disusun oleh (jabatan)**: Supervisor Finance
- **Disetujui oleh (jabatan)**: Direktur
- **Peta seluruh posisi**: [[REF - SOP Bharata 2026 per Posisi]]

## Daftar SOP

| No | Dokumen | No. dokumen | Tanggal |
|---|---|---|---|
| 1 | 051. SOP Input Data Penjualan di Sistem | 051/BK/SOP/IV/2025 | 23-Apr-2025 |

## Catatan Penyalinan

- Teks, urutan langkah, dan tabel disalin apa adanya, termasuk salah ketik di dokumen sumber. Tidak ada yang dirangkum atau ditambah.
- Nama orang di blok tanda tangan sengaja tidak disalin; yang dicatat hanya jabatannya.
- Flowchart berupa gambar: yang tersalin hanya teks kotaknya. Bentuk alur yang sah tetap di dokumen sumber.
- Kolom "No. dokumen" dan "Tanggal" diambil dari kop dokumen; kosong berarti kopnya tidak memuat nilai itu.

## 051. SOP Input Data Penjualan di Sistem

**Berkas sumber**: `051. SOP Input Data Penjualan di Sistem.docx` · **No. dokumen**: 051/BK/SOP/IV/2025 · **Revisi**: 00 · **Tanggal**: 23-Apr-2025 · **Disusun oleh**: Supervisor Finance · **Disetujui oleh**: Direktur

### Tujuan

Menetapkan standar dan langkah-langkah dalam proses input data penjualan ke dalam sistem untuk memastikan keakuratan pelaporan keuangan,manajemen stok dan penagihan.

### Ruang Lingkup

1. Seluruh penjualan barang yang dicatat dalam sistem perusahaan oleh tim administrasi penjualan (terkecuali Non Marketplace).

### Penanggung Jawab

1. Admin Penjualan bertanggung jawab menginput data penjualan berdasarkan dokumen valid
2. AR Leader bertanggung jawab review dan validasi data penjualan
3. Admin Penjualan bertanggung jawab monitor proses pengiriman

### Definisi

Persiapan dokumen, input data ke sistem, validasi & submit, rekap database penjualan, sinkronisasi dengan tim terkait.

### Rincian Prosedur

- Prosedur Persiapan Dokumen :
    1. Pastikan dokumen penjualan lengkap : Data order penjualan harian dalam bentuk excel setiap platform.
    2. Pastikan kesesuaian format data kebutuhan sistem keuangan
- Prosedur Input data ke sistem :
    1. Masuk ke sistem keuangan
    2. Upload data excel sesuai dengan platform
    3. Lakukan sync sales dengan memilih parameter :
        1. Invoice date
        2. Team/nama toko platform
        3. Status dari pesanan
        4. Rentan waktu pesanan itu di proses
        5. Lalu submit
    4. Lakukan sync hasil olah data(penjualan & sample) kedalam sistem accurate dengan cara:
        1. Masuk menu Daily Sales
        2. Pilih Sync With Accurate
        3. Pilih tanggal sesuai dengan no invoice yang sudah terbuat
        4. Lalu submit
- Prosedur Olah Data dengan Excel :
    1. Lakukan olah data platform KiriminAja dengan ketentuan sebagai berikut:
        1. Pastikan data yang diambil dari platform adalah dalam rentan waktu 3 hari.
        2. Filter data yang dibatalkan dan sesuai divisi
        3. Filter data penjualan berdasarkan jenis pesanan COD
        4. Pilih rentan waktu pesanan yang sesuai dengan tanggal pengiriman dan invoice.
        5. Lakukan analisis dengan pivot table untuk mengetahui qty dan produk.
        6. Lampirkan hasil olahan data pada Invoice Penjualan Harian.
        7. Input manual data penjualan ke sistem keuangan
- Prosedur Input Data Invoice ke Sistem:
    1. Masuk ke sistem Accurate
    2. Buat entri baru dan isi data berikut :
        1. Tanggal penjualan
        2. Nama pelanggan
        3. Produk
        4. Jumlah & harga satuan
        5. Informasi gudang
        6. Lengkapi data di Info Lainnya
        7. Pajak
        8. Terms pembayaran(TOP)
- Prosedur Validasi & Submit :
    1. Periksa kembali olahan data secara berkala.
    2. Minta AR Leader untuk memverifikasi data.
    3. Submit transaksi agar masuk ke sistem keuangan.
- Prosedur Cetak atau Simpan Bukti :
    1. Simpan invoice yang telah diinput sebagai excel
    2. Arsipkan secara sistematis sesuai nomor invoice di database penjualan
- Prosedur Sinkronisasi dengan Tim Terkait :
    1. Informasikan ke tim finance dan AR untuk proses penagihan
    2. Pastikan status pengiriman & pembayaran tercatat.

### Dokumen Pendukung atau Lampiran

6.1 Rekap Data Penjualan

6.2 Faktur/Invoice

### Distribusi Dokumen

1. Admin Penjualan
2. Supervisor Finance
3. Staff AR
4. AR Leader

### Flowchart Pengolahan dan Input Data Penjualan di Sistem

*Teks kotak flowchart, menurut urutan tersimpan di dokumen. Panah dan percabangan tidak ikut tersalin.*

1. Ambil Data Order dari Setiap Platform
2. Verifikasi Kelengkapan & Keakuratan Data
3. Olah Data Order Menjadi Invoice Penjualan
4. Input Data Invoice Penjualan ke Sistem Keuangan
5. Review & Validasi Data Input
6. Sinkronisasi Data Penjualan ke Sistem Accurate
7. Simpan Invoice dan Rekap di Database Penjualan

## Dokumen Terkait

- [[REF - SOP Bharata 2026 per Posisi]]

> **Status**: 🟢 **Diterima, 2026-10-03, oleh Finance** (jawaban "setuju" pada berkas tanya-jawab audit penerimaan, 2026-10-02/03; keputusan §1 dan §2 sebelumnya sudah dijawab lewat chat pada 2026-10-01 dan 2026-10-02). Penghapus INC (§6) dan kewenangan atas uang FO sudah dijawab; butir lain masih **TBD** (lihat "Belum Diputuskan"). **Belum ada kode**: kaskade FO belum menangani INC yang menjadi kosong, belum ada fungsi hapus INC, dan pesan "dokumen ada di Accurate" belum memeriksa ke Accurate.

## Untuk Manajemen

**Apa yang diputuskan.** Order yang ditandai FO (fake order) sesudah uangnya cair dan sesudah penerimaan (INC) dibukukan harus **dikeluarkan dari INC itu**: nominalnya dikurangi, dan bila seluruh order di INC itu FO, **INC dihapus**. FO juga **tidak boleh masuk penjualan**, jadi faktur harian yang memuatnya ikut dikoreksi atau dihapus. Alasan finance: kalau dibiarkan, uang yang sama terbukukan dua kali, karena FO diinput admin lain.

**Siapa yang terdampak.** Finance dan tim penjualan (faktur), serta tim IT yang memperbaiki sistemnya. Pelapor FO (finance lewat impor Excel, dan kelak marketing yang melapor langsung) tidak mengubah caranya bekerja.

**Kenapa perlu ditulis.** Sistem sudah mengecilkan INC yang berisi campuran FO dan order normal, tetapi **INC yang seluruh ordernya FO tidak bisa dikecilkan sampai nol**: catatan sistem berubah jadi `SKIPPED` bernominal nol sementara dokumen di Accurate tetap utuh, dan sistem tetap melaporkan "penerimaan diselaraskan". Pada 2026-10-02 finance menyatakan INC-INC itu sudah tidak ada di Accurate (dihapus manual), dan catatan sistem masih menyebutnya ada. Keputusan di sini menjadi dasar perbaikan kaskade dan perapian data.

**Apa yang tidak dijanjikan.**
- Keputusan ini **tidak mengubah angka historis** di Accurate. Perapian dokumen yang sudah ada dikerjakan terpisah, dengan dry-run, cadangan, dan dijalankan manusia.
- **INC yang harus dihapus dihapus oleh sistem, tetapi hanya setelah finance menekan konfirmasi.** Sampai fungsi itu ada, finance menghapus manual dan sistem hanya mencatat.
- Aturan untuk FO yang dilaporkan sesudah periode ditutup finance **belum diputuskan**.

**Perkiraan besaran kerja.** Sedang (estimasi, belum diukur): satu perubahan di kaskade FO, satu pemeriksaan keberadaan dokumen di Accurate, dan satu pekerjaan data sekali jalan. Deploy backend saja, tanpa layar baru.

## Deskripsi

*Penegasan perlakuan order FO yang baru ditandai sesudah INC cair: INC dikurangi atau dihapus, faktur dikoreksi atau dihapus, dengan urutan INC lebih dulu. Menutup celah kaskade FO untuk INC yang menjadi kosong.*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Path di repo**: `bip-erp/services/integration/internal/usecase/accurate_fake_order_cascade.go` (kaskade, perlu menangani INC kosong) · `bip-erp/services/integration/internal/usecase/accurate_receipt_usecase.go` (`dokumenAdaTakDitimpa`, perlu memeriksa ke Accurate) · `bip-erp/services/integration/internal/interface/http/invoice_correction_handler.go` (penandaan FO satuan dan impor massal)
- **Tanggal**: 2026-10-02
- **Pelacakan**: bip-erp#2199 (audit auto-sync penerimaan, dulu BHA-297)

## Context

1. **Cara FO ditandai.** Penandaan FO bisa satuan (`POST /accurate/orders/fake-order-override`) atau impor Excel massal (`.../bulk`). Setiap penandaan menjalankan kaskade yang mengecilkan dokumen Accurate: INC lebih dulu (kirim ulang sebagai penggantian penuh), lalu faktur harian. Faktur yang menjadi kosong di-VOID, sebagaimana tertulis di [[Microservices - Integration Service]].
2. **Alur finance: INC dibukukan lebih dulu, FO ditandai belakangan.** Finance menyatakan INC (income) dibukukan dulu dan FO ditandai kemudian (jawaban 2026-10-01). Marketing akan melapor FO langsung tanpa menunggu akhir bulan, jadi kaskade akan lebih sering berjalan dan tersebar sepanjang hari, bukan dalam gelombang.
3. **Yang terukur di prod (2026-09-28 sampai 2026-10-02).** Impor FO oleh finance pada 28 September, 29 September, dan 2 Oktober dini hari. Puluhan INC campuran berhasil dikecilkan oleh kaskade. Enam belas INC TikTok September yang seluruhnya berisi FO, batal, atau order di luar batas tanggal toko menghasilkan alokasi kosong: catatan sistem jadi `SKIPPED` bernominal nol, kaskade mencatat "penerimaan diselaraskan", dan tiga INC lain terkena hal yang sama dari impor 2 Oktober. Waktu penandaan diambil dari log audit `invoice_correction_logs`, bukan dari `updated_at` order (yang ikut berubah oleh proses lain).
4. **INC kosong tidak punya jalan keluar di kode.** Kode hanya punya `DeleteSalesInvoice` (faktur), tidak ada fungsi menghapus INC. Faktur bernol baris tidak pernah dikirim ulang, jadi isi lamanya bisa tertinggal di Accurate sebagai faktur hantu.
5. **Klaim "dokumen ada di Accurate" tidak diverifikasi.** Penjagaan yang mencegah INC `SKIPPED` ditimpa hanya bersandar pada `accurate_id` yang tersimpan. Pembacaan dokumen yang hilang mengembalikan kosong tanpa galat. Pada 2026-10-02 finance menyatakan 18 INC yang dibahas tidak ditemukan di Accurate, padahal catatan sistem menyebutnya ada.
6. **Dampak ke rekonsiliasi kas.** Menghapus INC mengurangi saldo kas toko di Accurate, sedangkan saldo marketplace tetap memuat uangnya. Itu menimbulkan selisih negatif di layar rekonsiliasi kas toko ([[Finance - Proses Rekonsiliasi Kas Toko dan Bank]]) sampai uang FO dibukukan ke akun yang sama.
7. **Jawaban finance.** (a) FO yang dilaporkan sesudah cair harus dikurangi atau dihapus, karena dibiarkan berarti dobel input. (b) FO memang seharusnya tidak masuk penjualan karena bukan penjualan. Finance hanya memeriksa keberadaan dokumen, bukan isi faktur, karena faktur adalah data penjualan.
8. **Jawaban finance 2026-10-02/03 (berkas tanya-jawab audit penerimaan).** (a) **Uang order FO cair** ke rekening toko dan dibukukan **accounting lewat jurnal umum**, jadi INC yang tetap memuat FO membukukan uang yang sama dua kali. (b) INC yang harus dihapus sebaiknya **dihapus sistem dengan tombol konfirmasi finance**, bukan manual di Accurate. (c) Siapa dan kapan 18 INC yang sudah hilang dihapus **tidak diketahui**. (d) Faktur kosong dan pencocokan faktur yang menyusut ditangani **tim Sales/AR**, bukan finance. (e) Receipt Juli sampai Agustus berstatus `FAILED` **boleh dirapikan di sistem**, asal tidak menyentuh data Accurate yang sudah sesuai. (f) Finance **hanya menerima** data FO dan tidak memasukkannya ke ERP.
9. **Siapa melapor FO.** Staf AR Sales mengunggah daftar FO (Excel) ke ERP. Marketing yang melapor FO langsung memberi datanya ke IT atau lewat admin sales; finance bukan penginput. Perubahan dokumen Accurate oleh sistem boleh otomatis, **dengan syarat tidak mengubah data lain yang sudah sesuai**.

## Decision

1. **FO yang dilaporkan sesudah uang cair mengeluarkan order itu dari INC.** INC dikurangi sebesar uang order FO; bila seluruh order di INC itu FO, INC **dihapus**. Dibiarkan bukan pilihan.
2. **FO tidak masuk penjualan.** Faktur harian yang memuat order FO dikoreksi sampai tanpa FO; faktur yang menjadi kosong dihapus (VOID), seperti keputusan faktur kosong yang sudah ada.
3. **Urutan: INC dulu, baru faktur.** Accurate menolak mengubah atau menghapus faktur yang masih ada pembayarannya, jadi dokumen yang membayar harus lebih dulu.
4. **FO yang dilaporkan sebelum INC disusun tidak masuk INC sama sekali.** Ini sudah perilaku sekarang (order FO dikeluarkan saat INC dibangun) dan tidak berubah.
5. **Hasil kaskade harus jujur.** Kaskade tidak boleh melaporkan "diselaraskan" bila INC yang kosong belum dihapus. Hasilnya dilaporkan sebagai butuh tindakan, dengan nomor dokumennya.
6. **INC kosong dihapus oleh sistem, dengan konfirmasi finance.** Penghapusan INC tidak bisa dibatalkan, jadi sistem tidak menghapus sendiri: ia menampilkan INC yang harus dihapus dan menghapusnya setelah finance mengonfirmasi, dengan jejak siapa dan kapan. Sampai fungsi itu ada, finance menghapus manual dan sistem tidak menimpa apa pun.
7. **Klaim keberadaan dokumen di Accurate wajib diperiksa ke Accurate**, bukan disimpulkan dari `accurate_id` yang tersimpan. Pesan "dokumen ada di Accurate, perlu keputusan finance" hanya boleh keluar bila dokumennya benar-benar terbaca.
8. **Perubahan otomatis hanya menyentuh order FO.** Dokumen Accurate yang sudah sesuai dan order lain di dalamnya tidak boleh berubah oleh kaskade FO (jawaban finance, §Context butir 8f).

## Belum Diputuskan (TBD)

- **Batas antara "dikecilkan otomatis" dan "dihapus dengan konfirmasi".** Tafsiran tim IT dari dua jawaban finance: mengecilkan INC yang masih memuat order normal berjalan otomatis, sedangkan menghapus INC yang seluruhnya FO menunggu konfirmasi. Belum dikonfirmasi finance.
- **Apakah faktur kosong boleh dihapus, dan faktur yang menyusut sesuai isinya.** Penanganannya diserahkan ke Sales/AR; jawaban boleh/tidak dan hasil pencocokan belum ada.
- **INC yang memuat order di luar batas tanggal toko** selain FO (dua INC pada 2026-10-02): apakah order itu sudah dibukukan manual terpisah. Belum dijawab.
- **INC yang tertahan di Kotak Adopsi** (isi Accurate berbeda dari sistem) dan memuat satu order FO: diputuskan lewat Kotak Adopsi, bukan lewat keputusan ini.
- **FO yang dilaporkan terlambat untuk periode yang sudah ditutup finance.** Finance pernah menyatakan periode Agustus tidak boleh diubah; jawaban 2026-10-03 hanya menjelaskan bahwa FO yang terlanjur masuk income biasanya terdeteksi lewat selisih (karena FO seharusnya diinput accounting), tanpa menjawab perlakuan di periode tertutup. Tetap TBD.

## Consequences

- **Perbaikan kaskade FO** menangani INC yang menjadi kosong sesuai butir 1 dan 5, dan fungsi hapus INC berkonfirmasi finance sesuai butir 6 (backend, ditambah satu tombol konfirmasi di layar finance).
- **Pemeriksaan keberadaan dokumen** di Accurate sebelum menulis pesan atau penjagaan "dokumen ada" (butir 7).
- **Perapian data sekali jalan** untuk catatan sistem atas INC yang sudah dihapus finance (ID Accurate basi, label gangguan lama, teks `last_error` lama). Dikerjakan dengan dry-run, cadangan, dan rollback, dijalankan manusia, dan baru sesudah finance memastikan INC-nya memang sudah dihapus.
- **Faktur yang seharusnya kosong** (faktur hantu) dikoreksi atau dihapus sesuai butir 2 dan 3, sesudah INC pembayarnya tiada.
- **Selisih rekonsiliasi kas toko TikTok** akan mengecil bila uang FO dibukukan ke akun kas toko yang sama dengan INC yang dihapus. Itu perkiraan dari urutan besarnya, belum diukur per akun.
- **Risiko**: penghapusan INC tidak bisa dibatalkan, jadi jalur apa pun yang melakukannya (sistem atau skrip) wajib memberi konfirmasi, mencatat siapa dan kapan, dan tidak boleh menjalankan penghapusan massal tanpa pratinjau.

## Dokumen Terkait

- [[Microservices - Integration Service]] · [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] · [[Finance - Proses Rekonsiliasi Kas Toko dan Bank]]
- [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]] · [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] · [[ADR - 0144 Retur yang Sudah Dibukukan Manual oleh Finance Ditandai per Order dan Dihormati Semua Jalur Auto-Sync]]
- [[ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris]] (rujuk dengan judul; nomor 0077 dipakai dua ADR)

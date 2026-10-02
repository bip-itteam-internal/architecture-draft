> **Status**: 🟡 **Diusulkan, menunggu konfirmasi finance** (2026-10-02). Dua butir keputusan (§1 dan §2) sudah dijawab finance lewat chat dan berkas balasan pada 2026-10-01 dan 2026-10-02; §6 dan beberapa butir lain masih **TBD** (lihat "Belum Diputuskan"). **Belum ada kode**: kaskade FO belum menangani INC yang menjadi kosong, dan pesan "dokumen ada di Accurate" belum memeriksa ke Accurate.

## Untuk Manajemen

**Apa yang diputuskan.** Order yang ditandai FO (fake order) sesudah uangnya cair dan sesudah penerimaan (INC) dibukukan harus **dikeluarkan dari INC itu**: nominalnya dikurangi, dan bila seluruh order di INC itu FO, **INC dihapus**. FO juga **tidak boleh masuk penjualan**, jadi faktur harian yang memuatnya ikut dikoreksi atau dihapus. Alasan finance: kalau dibiarkan, uang yang sama terbukukan dua kali, karena FO diinput admin lain.

**Siapa yang terdampak.** Finance dan tim penjualan (faktur), serta tim IT yang memperbaiki sistemnya. Pelapor FO (finance lewat impor Excel, dan kelak marketing yang melapor langsung) tidak mengubah caranya bekerja.

**Kenapa perlu ditulis.** Sistem sudah mengecilkan INC yang berisi campuran FO dan order normal, tetapi **INC yang seluruh ordernya FO tidak bisa dikecilkan sampai nol**: catatan sistem berubah jadi `SKIPPED` bernominal nol sementara dokumen di Accurate tetap utuh, dan sistem tetap melaporkan "penerimaan diselaraskan". Pada 2026-10-02 finance menyatakan INC-INC itu sudah tidak ada di Accurate (dihapus manual), dan catatan sistem masih menyebutnya ada. Keputusan di sini menjadi dasar perbaikan kaskade dan perapian data.

**Apa yang tidak dijanjikan.**
- Keputusan ini **tidak mengubah angka historis** di Accurate. Perapian dokumen yang sudah ada dikerjakan terpisah, dengan dry-run, cadangan, dan dijalankan manusia.
- **Belum diputuskan siapa yang menghapus INC**: sistem atau finance. Selama belum, finance menghapus manual dan sistem hanya mencatat.
- Belum dijawab apakah uang order FO benar-benar cair ke rekening (lihat TBD).

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

## Decision

1. **FO yang dilaporkan sesudah uang cair mengeluarkan order itu dari INC.** INC dikurangi sebesar uang order FO; bila seluruh order di INC itu FO, INC **dihapus**. Dibiarkan bukan pilihan.
2. **FO tidak masuk penjualan.** Faktur harian yang memuat order FO dikoreksi sampai tanpa FO; faktur yang menjadi kosong dihapus (VOID), seperti keputusan faktur kosong yang sudah ada.
3. **Urutan: INC dulu, baru faktur.** Accurate menolak mengubah atau menghapus faktur yang masih ada pembayarannya, jadi dokumen yang membayar harus lebih dulu.
4. **FO yang dilaporkan sebelum INC disusun tidak masuk INC sama sekali.** Ini sudah perilaku sekarang (order FO dikeluarkan saat INC dibangun) dan tidak berubah.
5. **Hasil kaskade harus jujur.** Kaskade tidak boleh melaporkan "diselaraskan" bila INC yang kosong belum dihapus. Hasilnya dilaporkan sebagai butuh tindakan, dengan nomor dokumennya.
6. **Siapa yang menghapus INC kosong: TBD** (lihat di bawah). Sampai diputuskan, finance menghapus manual dan sistem tidak menimpa apa pun.
7. **Klaim keberadaan dokumen di Accurate wajib diperiksa ke Accurate**, bukan disimpulkan dari `accurate_id` yang tersimpan. Pesan "dokumen ada di Accurate, perlu keputusan finance" hanya boleh keluar bila dokumennya benar-benar terbaca.

## Belum Diputuskan (TBD)

- **Penghapusan INC oleh sistem atau finance.** Opsi A: fungsi hapus INC baru di sistem, digerbang peran finance dan dengan konfirmasi (penghapusan tidak bisa dibatalkan). Opsi B: finance menghapus di Accurate, sistem mendeteksi dan menyelaraskan catatannya.
- **Apakah uang order FO benar-benar cair ke rekening.** [[Microservices - Integration Service]] menyatakan uang FO tidak masuk rekening toko dan dibukukan manual finance, tetapi contoh di dok yang sama mencatat order FO yang sudah cair. Jawabannya menentukan apakah mengecilkan INC sesuai dengan kas yang sebenarnya.
- **INC yang memuat order di luar batas tanggal toko** selain FO (dua INC pada 2026-10-02): apakah order itu sudah dibukukan manual terpisah.
- **INC yang tertahan di Kotak Adopsi** (isi Accurate berbeda dari sistem) dan memuat satu order FO: diputuskan lewat Kotak Adopsi, bukan lewat keputusan ini.
- **FO yang dilaporkan terlambat untuk periode yang sudah ditutup finance.** Finance pernah menyatakan periode Agustus tidak boleh diubah; keputusan ini tidak menjawab bagaimana FO terlambat diperlakukan di periode tertutup.

## Consequences

- **Perbaikan kaskade FO** menangani INC yang menjadi kosong sesuai butir 1 dan 5. Perubahan ini tergantung jawaban butir 6.
- **Pemeriksaan keberadaan dokumen** di Accurate sebelum menulis pesan atau penjagaan "dokumen ada" (butir 7).
- **Perapian data sekali jalan** untuk catatan sistem atas INC yang sudah dihapus finance (ID Accurate basi, label gangguan lama, teks `last_error` lama). Dikerjakan dengan dry-run, cadangan, dan rollback, dijalankan manusia, dan baru sesudah finance memastikan INC-nya memang sudah dihapus.
- **Faktur yang seharusnya kosong** (faktur hantu) dikoreksi atau dihapus sesuai butir 2 dan 3, sesudah INC pembayarnya tiada.
- **Selisih rekonsiliasi kas toko TikTok** akan mengecil bila uang FO dibukukan ke akun kas toko yang sama dengan INC yang dihapus. Itu perkiraan dari urutan besarnya, belum diukur per akun.
- **Risiko**: penghapusan INC tidak bisa dibatalkan, jadi jalur apa pun yang melakukannya (sistem atau skrip) wajib memberi konfirmasi, mencatat siapa dan kapan, dan tidak boleh menjalankan penghapusan massal tanpa pratinjau.

## Dokumen Terkait

- [[Microservices - Integration Service]] · [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] · [[Finance - Proses Rekonsiliasi Kas Toko dan Bank]]
- [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]] · [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] · [[ADR - 0144 Retur yang Sudah Dibukukan Manual oleh Finance Ditandai per Order dan Dihormati Semua Jalur Auto-Sync]]
- [[ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris]] (rujuk dengan judul; nomor 0077 dipakai dua ADR)

# ANALISA - Retur Dibukukan Manual oleh Finance

Papan kerja hasil `/analisa-kebutuhan` 2026-09-30. Keputusan dan alasannya di [[ADR - 0144 Retur yang Sudah Dibukukan Manual oleh Finance Ditandai per Order dan Dihormati Semua Jalur Auto-Sync]]; cara kerjanya di [[Microservices - Integration Service]].

Kebutuhan: finance yang sudah membukukan Retur Penjualan sendiri di Accurate untuk sebuah order harus bisa membuat sistem berhenti menyentuh retur order itu, dan tandanya bertahan terhadap sinkronisasi, sweep, dan Retry. Yang diminta manajemen semula "penandaan manual yang bertahan"; kebutuhannya sebenarnya menghentikan pembukuan ganda dengan keputusan yang bisa diperiksa.

Urutan di bawah mengikuti dependensi. Tiap item ditulis supaya bisa langsung dilempar ke `/start-task`. Semua repo kode wajib PR; deploy prod dijalankan manusia; backend naik sebelum frontend.

## T1 · Penanda per order dan penjagaan di satu fungsi keputusan
- **Isi**: field penanda di `transaction_orders` (aktif, alasan, nomor Retur Penjualan, siapa, kapan, dan jejak pencabutan; tak dihapus saat dicabut), tidak disentuh sinkronisasi marketplace. `returTakDibukukan` menilainya. Test satu per jalur yang mengunci order bertanda tak melahirkan atau menghidupkan baris: `SyncOrderReturn`, `rebuildAndSendGroup`, `RetryDailyReturn` (termasuk Retry manual), konfirmasi scan gudang, `DropFakeOrderReturn`. Test kontrol negatif: tanpa penanda, perilaku lama tetap. Test bahwa keterangan `SKIPPED` bertanda tidak cocok regex penyembunyi di daftar.
- **Repo**: bip-erp (integration)
- **Bergantung**: — (PR #2414 sudah merged)
- **Selesai bila**: order bertanda yang punya baris `PENDING`, `FAILED`, atau `SKIPPED` tidak dibukukan oleh jalur mana pun, dan ordernya tetap berjejak `SKIPPED` tanpa menutup order lain di keranjang yang sama.
- `/start-task Penanda retur dibukukan manual per order di transaction_orders dan penjagaan di returTakDibukukan (ADR-0144 §1-3)`

## T2 · Endpoint tandai dan cabut
- **Isi**: endpoint di `/accurate/orders/...` untuk menandai dan mencabut, digerbang `returselisih.tandai`, identitas dicap server dari header gateway, alasan dan nomor Retur Penjualan wajib, jejak lewat pola audit koreksi order yang ada. Menolak bila order sudah anggota baris `SENT` (menyebut nomor dokumen sistem). Saat menandai, baris hidup yang memuat order langsung dipisah ke jejak `SKIPPED` (memakai mekanisme pemisahan per order yang ada) tanpa menunggu siklus berikutnya. Test lewat Fiber untuk jalur galat (tanpa izin, tanpa alasan, sudah `SENT`), bukan hanya fungsi murni.
- **Repo**: bip-erp (integration)
- **Bergantung**: T1
- **Selesai bila**: dipanggil **lewat gateway** dengan tiga token (finance, pengguna tanpa izin, header hilang) → 200 / 403 / 403; tanpa alasan → 400; order berbaris `SENT` → ditolak dengan nomor dokumen.
- `/start-task Endpoint tandai dan cabut retur dibukukan manual, digerbang returselisih.tandai, dengan audit (ADR-0144 §4-7)`

## T3 · Aksi di layar Auto-Sync Retur
- **Isi**: tombol "Tandai sudah dibukukan manual" di detail baris atau order, dialog dengan alasan dan nomor Retur Penjualan wajib (acuan pola: `VoidAdjustmentDialog` di `receipt-adjustments-section.tsx`), tampilan penanda di modal detail (siapa, kapan, nomor dokumen), aksi cabut dengan peringatan bahwa dokumen manual di Accurate harus sudah dihapus. Aksi mengikuti izin. Teks lewat i18n id+en ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]). Keterangan dari backend ditampilkan apa adanya (tanpa pencocokan teks baru).
- **Repo**: erp-frontend
- **Bergantung**: T2 (deploy backend dulu)
- **Selesai bila**: satu perjalanan utuh di browser sebagai finance: buka baris, tandai, baris berlabel DILEWATI dengan keterangan nomor dokumen, cabut. Pengguna tanpa izin tak melihat aksinya.
- `/start-task Aksi tandai retur dibukukan manual di layar Auto-Sync Retur (ADR-0144)`

## T4 · Ukur volume di prod lalu tandai ulang order yang sudah ditutup lewat skrip
- **Isi**: (a) skrip mongosh **baca-saja** menghitung baris `SKIPPED` yang keterangannya bukan templat mesin (kandidat penutupan manual) dan order yang punya baris `SKIPPED` sekaligus baris hidup (bukti baris yang bocor); dijalankan manusia. (b) Perkakas sekali jalan di `cmd/` yang menandai daftar order dari finance: dry-run default, `--apply` wajib `--cadangan` dan `--alasan`, daftar kosong ditolak, memakai jalur yang sama dengan endpoint (bukan menulis langsung), stempel penanda `cli:<operator>`. Dijalankan manusia.
- **Repo**: bip-erp (integration)
- **Bergantung**: T2 sudah ter-deploy di prod
- **Selesai bila**: tiap order yang sudah ditutup manual sebelum ADR ini bertanda, dan sinkronisasi terjadwal berikutnya tidak menghidupkannya (dibuktikan dengan membandingkan status baris sebelum dan sesudah satu siklus).
- `/start-task Perkakas menandai ulang order yang sudah dibukukan manual dan skrip ukur volume (ADR-0144, Consequences)`

## T5 · Daftar dan ekspor order bertanda
- **Isi**: daftar order bertanda dengan filter dan unduh Excel (siapa, kapan, alasan, nomor dokumen), agar salah tandai dapat ditemukan. Bergabung dengan pola ekspor yang ada di layar retur.
- **Repo**: bip-erp (integration) · erp-frontend
- **Bergantung**: T2, T3
- **Selesai bila**: finance dapat mengekspor semua order bertanda satu periode dan mencocokkannya dengan dokumen manual di Accurate.
- `/start-task Daftar dan ekspor order retur bertanda dibukukan manual (ADR-0144, Consequences)`

## T6 · Verifikasi lewat gateway dan prod (manusia yang deploy)
- **Isi**: deploy integration-service (backend dulu, lalu frontend) oleh manusia; verifikasi lewat gateway satu perjalanan: finance menandai satu order nyata, tunggu satu siklus sinkronisasi (sekitar 2 jam) dan buktikan baris tidak hidup kembali, lalu cabut dan buktikan order kembali ke alur normal. Angka nol yang mencurigakan diperlakukan sebagai pertanyaan.
- **Bergantung**: T3, T4
- `/start-task Verifikasi prod penanda retur dibukukan manual lewat gateway (ADR-0144)`

## Tahap 2 (belum diputuskan, tidak dikerjakan sekarang)
- Verifikasi nomor Retur Penjualan ke Accurate saat menandai (dokumen ada, mengacu faktur dan barang order yang sama) memakai klien detail retur yang sudah ada.
- Pemindai order berkandidat manual (retur Accurate di faktur order yang tak ditunjuk baris ERP mana pun) yang **menahan dan meminta konfirmasi manusia**, tidak menandai sendiri; bergabung dengan tahap 2 [[ADR - 0104 Selisih Retur Dihitung Terjadwal per Periode dan Bisa Ditandai Beres]].

## Titik yang belum tertutup dan sengaja di luar daftar ini
- Retry duplikat (`grupLainYangSudahMembukukan`) masih menulis keputusan satu order ke seluruh baris; brief lanjutan terpisah.
- Keranjang `TUNGGU` berstatus `SKIPPED` yang dihidupkan lagi oleh order sefaktur berikutnya (sudah ada sebelum PR #2414).

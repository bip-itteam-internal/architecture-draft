> **Status**: 🟡 **Diusulkan** (2026-09-30), disetujui pemilik proses (opsi A dari analisis kebutuhan), **kode belum ada**. Dua asumsi belum dikonfirmasi pemilik proses dan ditandai di Decision §5 dan §6: siapa yang boleh menandai, dan apakah nomor Retur Penjualan wajib.

## Untuk Manajemen

**Apa yang berubah di layar.** Di layar Auto-Sync Retur, finance mendapat satu aksi baru: **"Tandai sudah dibukukan manual"** pada sebuah order. Finance wajib mengisi alasan dan nomor Retur Penjualan yang sudah ia buat sendiri di Accurate. Sesudah itu sistem berhenti menyentuh retur order tersebut, lewat jalur apa pun (sinkronisasi otomatis tiap beberapa jam, kirim ulang, sweep, konfirmasi scan gudang), dan barisnya tampil "DILEWATI" beserta nomor dokumen dan siapa yang menandai. Tanda bisa dicabut, juga dengan alasan wajib dan tercatat.

**Siapa yang terdampak.** Finance menandai sendiri, tanpa menunggu IT. Tim IT tidak lagi menutup baris satu per satu lewat skrip, dan yang lebih penting: baris yang sudah ditutup tidak lagi hidup kembali dan tidak lagi berisiko membukukan retur yang sama dua kali di Accurate. Admin gudang tidak melihat perubahan apa pun.

**Apa yang tidak dijanjikan.**
- Sistem **tidak mendeteksi sendiri** bahwa finance sudah membukukan retur manual. Finance yang harus menandai; order yang lupa ditandai tetap bisa dibukukan sistem.
- Pada tahap pertama nomor dokumen **tidak dicek ke Accurate**, hanya dicatat.
- Bila sistem sudah lebih dulu membukukan retur order itu, penandaan **ditolak**: dokumen gandanya harus dibereskan finance di Accurate lebih dulu.
- Retur ganda yang sudah terlanjur terbukukan tidak diperbaiki oleh keputusan ini.
- Mencabut tanda tidak menghapus dokumen manual di Accurate. Sesudah dicabut sistem boleh membukukan order itu lagi, jadi finance wajib memastikan dokumen manualnya sudah dihapus lebih dulu.

**Perkiraan besaran kerja.** Sedang: sekitar satu minggu kerja untuk satu backend, satu layar, dan satu pekerjaan sekali jalan menandai ulang order yang sebelumnya ditutup lewat skrip (estimasi, belum diukur). Deploy backend lebih dulu, baru layar.

## Deskripsi

*Retur sebuah order yang sudah dibukukan finance secara manual di Accurate ditandai sebagai penanda per ORDER yang dibaca oleh fungsi keputusan yang sama dengan order fake/dikecualikan, sehingga seluruh jalur Auto-Sync Retur menghormatinya tanpa penjaga baru di tiap jalur. Menutup celah bahwa baris `SKIPPED` bukan penanda dan bisa dihidupkan lagi oleh sinkronisasi terjadwal.*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Path di repo**: `bip-erp/services/integration/internal/domain/entity/transaction.go` (field penanda, baru) · `bip-erp/services/integration/internal/usecase/accurate_rts_usecase.go` (`returTakDibukukan`, diperluas) · `bip-erp/services/integration/internal/handler/` (endpoint tandai dan cabut, baru) · `erp-frontend/src/features/integration/accurate/auto-sync-return/components/` (dialog tandai, baru)
- **Tanggal**: 2026-09-30

## Context

Finance kadang membukukan Retur Penjualan sendiri di Accurate untuk sebuah order (mis. `586056624755541056` dan `260908GBTJVJSN`, 30 September 2026). Agar sistem tidak membukukannya lagi, baris retur order itu ditutup jadi `SKIPPED` lewat skrip mongosh sekali jalan yang dijalankan manusia. Tandanya tidak bertahan: pada 30 September baris itu aktif kembali dan berisiko membukukan dokumen ganda.

Ditelusuri di `origin/main` `9c3a81bb`:

1. **`SyncOrderReturn` tidak pernah menolak baris `SKIPPED`.** Ia mencari baris lewat `GetByMember`, yang tidak menyaring status. `GetOrCreate` mencari berdasarkan kunci tanpa melihat status. Kalau kunci grup yang dihitung sama dengan kunci baris `SKIPPED`, baris itu dipakai ulang; kalau berbeda, dibuat baris `PENDING` baru dan baris `SKIPPED` ditinggal.
2. **Penimpaan status tidak bersyarat.** Jalur "ditahan menunggu gudang" menulis `PENDING` lewat `UpdateStatus` (`$set` by `_id`, tanpa cek status) sehingga status dan alasan penutupan hilang. Bila tidak ada penahan gudang, `rebuildAndSendGroup` bisa langsung membukukan dan menulis `SENT`.
3. **Baris `SKIPPED` bukan penanda, hanya jejak.** [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] menyatakan baris itu "inert bagi seluruh proses terjadwal"; kenyataannya inert hanya bagi pembaca (laporan, anomaly check), tidak bagi penulis. [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]] sudah mencatat `SKIPPED` yang hidup lagi lewat adopsi kunci (kambuh 2026-09-01).
4. **Tak ada pemeriksaan ke Accurate** sebelum membukukan retur, dan tak ada pemindai drift yang mencakup retur (yang ada, `pembalikanTakDikenal` di CLI, per faktur sehingga tidak dapat menunjuk order).
5. **Yang sudah ada dan bisa dipakai ulang.** `transaction_orders` sudah memuat penanda per order yang diisi manusia dan tak disentuh sync marketplace (`invoice_excluded`, `fo_override`, `warehouse_override`). Fungsi `returTakDibukukan` membacanya di dua titik: gerbang pertama `SyncOrderReturn` dan penyaring `rebuildAndSendGroup`. PR #2414 (merged 2026-09-30) menjadikan order yang kena keputusan `SKIPPED` dipisah ke baris jejak sendiri tanpa menutup keranjang milik order lain. Izin `returselisih.tandai` (finance saja, [[ADR - 0104 Selisih Retur Dihitung Terjadwal per Periode dan Bisa Ditandai Beres]] T1) sudah ada di katalog.
6. **Rute `/accurate/daily-returns/*` dan `/accurate/orders/*` tidak memakai gerbang peran** ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]: gateway hanya menjamin pemanggil sudah login), jadi tiap endpoint tulis baru wajib menggerbang dirinya sendiri.
7. **Vault tidak mengatur kasus ini.** [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] dan [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] mengasumsikan "era manual finance" berakhir sebelum 1 Juli. [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] mengakui 15 order dan 86 faktur yang ditambal manual sesudahnya, tanpa mekanisme penandaan di baris.

Yang belum terbukti dan tidak menggeser keputusan ini: proses terjadwal mana yang menghidupkan baris pada 30 September. Kode membuktikan `recover-tiktok-returns` berjalan tiap 2 jam pada menit :30 (`tiktok_returns_recover_task.go:52`); jadwal aktual di prod dan apakah kasusnya kunci-sama atau kunci-beda belum dibaca dari data prod. Penjaga di bawah bekerja sebelum baris mana pun ditulis, jadi kedua kasus tertutup.

## Decision

### 1. Penanda per ORDER di `transaction_orders`, field TERPISAH dari `invoice_excluded`

Field baru memuat: status aktif, alasan, nomor Retur Penjualan Accurate, siapa yang menandai dan kapan, dan bila dicabut siapa, kapan, dan alasannya. Tanda tidak dihapus saat dicabut (jejak tetap).

Tidak memakai ulang `invoice_excluded`: artinya mengeluarkan order dari FAKTUR, sedangkan order ini sudah difakturkan, dan menyalakannya mengubah snapshot faktur harian. Satu penanda per sejarah berbeda, alasan yang sama dengan `LepasTanpaScan` di [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]. Sync marketplace tidak boleh menyentuh field ini; penjaganya sama dengan `fo_override` (perakit himpunan sinkronisasi tidak memuatnya), dan dikunci test.

### 2. SATU fungsi keputusan, dibaca semua jalur

Penanda aktif dinilai di dalam `returTakDibukukan`, fungsi yang sama dengan order dikecualikan dan fake order. Karena fungsi itu sudah menjadi gerbang pertama `SyncOrderReturn` dan penyaring `rebuildAndSendGroup`, maka sinkronisasi terjadwal, webhook, Retry (termasuk Retry manual dari layar), sweep, konfirmasi scan gudang, dan pembersihan fake-order menghormatinya dari satu tempat. **Dilarang** menambah penjaga "cek penanda" terpisah di tiap jalur: itu melahirkan salinan aturan yang menyimpang. Satu test per jalur mengunci bahwa jalur itu tidak melahirkan atau menghidupkan baris untuk order bertanda.

Retry manual **tidak menembus** penanda. Ini berbeda dari penahan `BOOKED_EXTERNALLY` di [[ADR - 0065 Payout yang Sudah Dibukukan Dokumen Lain Ditutup, Bukan Dibuat Ulang]] yang menembus Retry manual: di sini keputusannya berasal dari manusia dan bersifat per order, dan menembusnya berarti membukukan dokumen ganda.

### 3. Efek pada baris yang ada

Order bertanda tetap **berjejak** ([[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] amandemen 2026-08-05: keputusan SKIP wajib berjejak): sistem menulis baris jejak `SKIPPED` per order dan mengeluarkan order itu dari keranjang bersama, tanpa menutup order lain di keranjang yang sama (mekanisme PR #2414). Keterangan menyebut order, nomor Retur Penjualan, dan penandanya. **Teks keterangan tidak boleh memuat kata yang cocok dengan penyembunyi `SKIPPED` di daftar** (`digantikan`, `Duplikat baris`, `digabung ke grup tanggal gudang`), karena baris bertanda harus terlihat oleh finance; dikunci test.

### 4. Penandaan ditolak bila sistem sudah lebih dulu membukukan

Bila order itu sudah menjadi anggota baris `SENT`, endpoint menolak dan menyebut nomor dokumen sistem. Menandai di atas dokumen sistem tidak menghapus dokumen ganda dan hanya menyembunyikannya. Gagal-tertutup: yang kelihatan finance adalah penolakan, bukan tanda yang menipu.

### 5. Siapa yang boleh menandai dan mencabut: finance saja (ASUMSI)

Gerbang izin `returselisih.tandai` yang sudah ada ([[ADR - 0104 Selisih Retur Dihitung Terjadwal per Periode dan Bisa Ditandai Beres]] T1), diterapkan di rute endpoint baru. **Asumsi**: pemilik proses belum menjawab pertanyaan "siapa"; dipakai rekomendasi finance saja tanpa membuat izin baru. Bila kelak perlu memisahkan penanda retur dari penanda selisih, izin dipecah pada saat itu, bukan sekarang.

Identitas penanda **dicap server** dari header gateway, tidak dari body: jejak yang bisa dipalsukan bukan jejak audit ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] #6). Endpoint hidup di `/accurate/orders/...` berdampingan dengan koreksi order yang sudah ada dan memakai pola audit yang sama.

### 6. Alasan dan nomor Retur Penjualan WAJIB (ASUMSI)

Tanpa alasan atau nomor dokumen, permintaan ditolak. **Asumsi**: pertanyaan "wajib nomor dokumen?" belum dijawab pemilik proses; dipakai rekomendasi wajib, karena kesalahan arah sebaliknya (retur tak pernah dibukukan sistem padahal finance keliru menandai) tak terlihat dan hanya ketahuan berminggu-minggu kemudian. Pada tahap pertama nomor hanya dicatat; verifikasi bahwa dokumen itu ada di Accurate dan mengacu ke faktur order yang sama adalah tahap kedua, bukan syarat.

### 7. Pencabutan

Endpoint yang sama, izin yang sama, alasan wajib, tercatat. Efeknya hanya melepas penanda: pada siklus berikutnya order kembali ke alur normal dan **boleh dibukukan sistem**. Sistem tidak dapat memeriksa apakah dokumen manual di Accurate sudah dihapus. Dialog pencabutan wajib memperingatkannya, dan tanggung jawab itu ada pada finance.

### 8. Yang SENGAJA tidak dilakukan

- **Bukan penjaga "baris `SKIPPED` tak boleh ditimpa"** di `SyncOrderReturn`. Itu hanya menutup satu dari dua kasus (baris baru tetap lahir) dan mematikan evaluasi ulang yang sah untuk `SKIPPED` gerbang payout.
- **Bukan deteksi otomatis per faktur** di jalur runtime. Faktur harian menampung banyak order dan retur manual tidak membawa penunjuk order, jadi deteksi tak dapat menunjuk order dan akan salah tahan. Boleh menjadi lapis kedua kelak, bukan pengganti tanda manusia.
- **Bukan gerbang peran untuk seluruh rute `/accurate/daily-returns/*`.** Di luar cakupan; yang digerbang hanya endpoint baru.

## Consequences

### Yang membaik

- Baris yang ditutup karena input manual tidak lagi hidup kembali, dan tak ada lagi baris baru yang lahir untuk order itu. Risiko dokumen Retur Penjualan ganda di Accurate (yang tak bisa dibatalkan otomatis; stok bertambah dua kali dan penjualan terbalik dua kali, lihat [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]]) tertutup untuk order bertanda.
- Finance tidak lagi bergantung pada IT untuk menutup baris, dan tak ada lagi skrip sekali jalan yang menulis ke prod untuk keperluan ini.
- Ada jawaban tunggal atas "kenapa order ini dilewati": penanda, siapa, kapan, dokumen apa.
- Keputusan `SKIPPED` untuk satu order tidak lagi menutup keranjang order lain (PR #2414) dan kini punya sumber keputusan manusia yang bertahan.

### Yang memburuk atau tetap terbuka

- ⚠️ **Tanda bergantung pada disiplin finance.** Order yang dibukukan manual tetapi tak ditandai tetap bisa dibukukan sistem. Yang menahan hanya kebiasaan kerja dan daftar order bertanda; pemindai otomatis (tahap 2, di [[ADR - 0104 Selisih Retur Dihitung Terjadwal per Periode dan Bisa Ditandai Beres]]) belum ada.
- ⚠️ **Salah menandai tak terlihat.** Retur order yang keliru ditandai tak pernah dibukukan sistem dan tak ada galat. Dimitigasi alasan dan nomor dokumen wajib, jejak lengkap, dan daftar order bertanda yang harus dapat diekspor (task terpisah).
- **Order yang sudah ditutup lewat skrip sebelum ADR ini tidak punya tanda** dan tetap rentan sampai ditandai ulang sekali. Perlu pekerjaan sekali jalan, dijalankan manusia (dry-run dulu, cadangan, `--apply` hanya sesudahnya).
- **Retur yang dibukukan sistem lebih dulu lalu ditambal manual** tidak tertangani: penandaan ditolak (§4) dan finance harus membereskan dokumennya di Accurate.
- Dok [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] menyatakan baris `SKIPPED` "inert bagi seluruh proses terjadwal". Pernyataan itu hanya berlaku bagi pembaca; keputusan ini tidak mengubah baris `SKIPPED` menjadi penanda, ia menambah penanda di order.
- Label "DILEWATI" di layar retur masih tertulis mentah (tidak lewat i18n). Teks baru fitur ini wajib lewat i18n id+en ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]); label lama tidak diubah di sini.

### Deploy

- Hanya integration-service naik; tak ada env baru, field baru berbentuk `omitempty` sehingga tak ada migrasi. Ada endpoint baru, jadi **backend sebelum frontend** (frontend aman bila field belum ada).
- Deploy prod dijalankan manusia; agent hanya menyiapkan daftar container, urutan, dan gerbang verifikasi. Verifikasi wajib satu perjalanan utuh lewat gateway: finance menandai satu order, sinkronisasi berikutnya tidak menghidupkannya, lalu pencabutan mengembalikannya ke alur normal.

### Belum diukur (asumsi eksplisit)

- Jumlah order yang dibukukan manual per minggu belum diukur di prod (tak ada akses baca dari sesi analisis). Skrip mongosh baca-saja untuk mengukurnya ada di daftar task. Yang tercatat dari lapangan: puluhan order ditutup dalam satu hari kerja pada 30 September 2026.

## Dokumen Terkait

- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] · [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]] · [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]]
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] tentang stempel penginput dan `LepasTanpaScan`
- [[ADR - 0065 Payout yang Sudah Dibukukan Dokumen Lain Ditutup, Bukan Dibuat Ulang]] · [[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]] · [[ADR - 0104 Selisih Retur Dihitung Terjadwal per Periode dan Bisa Ditandai Beres]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
- [[Microservices - Integration Service]] · [[Finance - Proses Retur dan Piutang Marketplace]] · [[APP - Web ERP]]
- [[ANALISA - Retur Dibukukan Manual oleh Finance]] (daftar task)

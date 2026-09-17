# ADR - 0108 Monitoring Sesi Live di Web Hanya Baca untuk Leader dan Live Support

## Deskripsi

*Web ERP kembali punya layar sesi live per sesi, kali ini **hanya baca**: sesi yang sedang berjalan dan riwayat per sesi dengan rincian lengkap. Leader marketing melihat seluruh toko beserta angka penjualan; jabatan **Live Support** melihat toko departemennya tanpa angka. Mencatat, menjeda, mengakhiri, dan mengambil alih sesi tetap hanya di MyBharata.*

- **Status**: ⚠️ **Merged 2026-09-18, di DEV, belum PROD.** Kode: bip-erp [#1966](https://github.com/bip-itteam-internal/bip-erp/pull/1966) `feat/marketing-analytics-monitoring-sesi-live` (merged 01:04 WIB) dan erp-frontend [#1643](https://github.com/bip-itteam-internal/erp-frontend/pull/1643) `feat/monitoring-sesi-live` (merged 01:12 WIB). Test hijau di keduanya; layar diverifikasi di Chrome atas hasil build dengan API tiruan (leader, Live Support, ponsel 390px mode gelap bahasa Inggris, 403, toko kosong). **DEV terverifikasi lewat gateway 2026-09-18 01:15 WIB**: biner container memuat literal rute (kontrol negatif rute karangan 0), `GET /api/marketing-analytics/live-support/sesi/berjalan` dan `/live-support/sesi?dari&sampai` membalas **200** `{"lingkup":"semua","rows":[],"toko_kosong":false}` untuk akun ber-`it: staff`, tanpa rentang **400**, akun non-pemantau **403**, rute karangan **404**. ⚠️ `rows` kosong karena **`live_shifts` di DEV berisi 0 dokumen** (terukur langsung di Mongo dev, koleksinya ada), bukan rantai putus. Frontend DEV belum ter-deploy saat dicek (container `frontend-hris-dashboard` masih build satu jam sebelumnya), jadi layarnya belum pernah dibuka terhadap backend sungguhan.
- **Tanggal**: 2026-09-17
- **Terkait**: [[Microservices - Marketing Analytics Service]] · [[API - Marketing Analytics Service]] · [[APP - Web ERP]] · [[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]] · [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]]

## Untuk Manajemen

- **Yang berubah di layar**: menu baru **Monitoring Sesi Live** di Marketing → Live Support. Isinya dua tab: **Sedang Berjalan** (kartu per sesi: akun, toko, host, Live Support, ceklis kesiapan, durasi, status jeda, lencana bila sesi sudah melewati batas shift, dan GMV sementara untuk leader) dan **Riwayat** (tabel per sesi, maksimal 92 hari per tampilan). Klik satu sesi membuka rinciannya: siapa yang bertugas beserta status jadwalnya, ceklis kesiapan beserta catatannya, porsi GMV per host, dan linimasa mulai, tiap jeda, permintaan ambil alih, sampai cara sesi berakhir.
- **Siapa terdampak**: leader marketing (SPV Kyura dan Beauty Hacks, leader iklan, supervisor integrasi, seluruh anggota IT) dan pemegang jabatan Live Support. Host tidak mendapat menu ini; riwayat miliknya tetap di MyBharata.
- **Tidak dijanjikan**: tidak ada tombol apa pun yang mengubah sesi di web. Leader tetap tidak bisa mengakhiri sesi orang lain (keputusan 2026-08-30), dan sesi yang perlu koreksi tetap dibetulkan lewat skrip oleh tim IT. Live Support tidak melihat angka penjualan.
- **Besaran kerja**: sedang. Dua rute baca baru di marketing-analytics dan satu halaman web. Tanpa env baru, tanpa index baru, tanpa perubahan MyBharata. Deploy `marketing-analytics-service` lalu `frontend-hris`.

## Context

1. **[[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]] menghapus halaman web Sesi Live Host (2026-09-11)** dan mencatat konsekuensinya: leader tak punya lagi riwayat per sesi seluruh tim di layar mana pun, dan membukanya kembali adalah keputusan baru. Analisis Live dan panel ICC hanya ringkasan per orang; MyBharata hanya sesi milik sendiri.
2. **[[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] mencatat Live Support tak punya layar untuk melihat sesi** yang mencatatnya sebagai pendukung.
3. **Backend sudah mengirim hampir seluruh isi rincian.** `GET /live-shifts` (riwayat) membawa dokumen sesi utuh plus ringkasan penjualan dari `RingkasShiftBanyak`. Yang belum ada hanya nama toko.
4. **Live Support tak bisa memakai rute `/live-shifts*`.** Seluruhnya digerbang middleware `common.RequireLiveShiftUser` (peran `insentive: host_live` atau leader marketing), sedangkan pemegang jabatan Live Support di produksi tak punya `system_roles` sama sekali (diukur 2026-09-17). Gerbang yang sama juga menjaga Mulai, Jeda, Akhiri, dan Ambil alih, dan kontraknya dibaca MyBharata.
5. **Non-leader sengaja tak melihat kinerja rekan**: `GET /live-shifts/performa` digerbang `RequireMarketingLeader`, riwayat non-leader dipaksa ke dirinya sendiri.

## Decision

1. **Pengguna: leader marketing DAN jabatan Live Support.** Predikat leader `common.IsMarketingLeader`, sama dengan riwayat `/live-shifts` seluruh tim ([[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] §6, termasuk staf IT). Jabatan dicocokkan `common.PosisiCocok(c, "Live Support")`, konstanta yang sama dengan setoran karya ([[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]]). Leader diperiksa lebih dulu, jadi orang yang lolos keduanya mendapat lingkup yang lebih luas. Host tidak.
2. **Lingkup Live Support: seluruh sesi di toko departemennya, di semua channel, TANPA angka penjualan.** Toko dari `department_shops` dengan `department` dari header gateway dicocokkan persis. Angka **tidak dihitung dan tidak dikirim server** (`penjualan: null`), dan sesi TikTok tidak dibaca sama sekali untuk lingkup ini. Menyembunyikan angka di layar saja tidak diterima.
3. **Lingkup leader: seluruh sesi seluruh toko beserta angka**, sama dengan riwayat leader hari ini. Nama toko gagal dibaca tidak menggagalkan layar leader.
4. **Hanya baca.** Tidak ada Mulai, Jeda, Akhiri, Ambil alih, maupun koreksi di web. Keputusan ADR 0091 tentang klien pencatat tidak berubah.
5. **Rute baca baru, bukan memperluas `/live-shifts`**: `GET /live-support/sesi/berjalan` dan `GET /live-support/sesi?dari&sampai`, gerbang di handler. Rute `/live-shifts*`, gerbangnya, dan kontraknya tidak disentuh.
6. **Rincian = data catatan sesi + total TikTok yang sudah dihitung.** Tanpa rincian per sesi TikTok yang dijodohkan; tanpa laba kotor (selalu 0).
7. **Rute sesi berjalan TIDAK menjalankan tutup otomatis saat dibaca**, beda dari `/live-shifts/berjalan`. Layar dibuka banyak orang dan diperbarui tiap 60 detik, sedangkan penutupan itu memanggil attendance per sesi. Tik 10 menit tetap menutupnya; baris membawa `batas_tutup_otomatis` (dari `batasTutupShift`, satu perumus dengan penutupan dan pengingatnya) sehingga layar menandai sesi yang sudah lewat batas.
8. **Rincian dibuka sebagai panel samping** dari baris yang sudah dimuat, tanpa rute baca satu sesi, supaya tanda perlu koreksi tetap hasil deteksi tumpang tindih atas seluruh rentang. Panel diikat ke ID sesi dan membaca baris terkini tiap pembaruan, sehingga durasinya sama dengan kartunya.
9. **Rute riwayat hanya menerima rentang tanggal.** Saringan toko, host, dan cara selesai dikerjakan layar atas baris yang dimuat.
10. **Status permintaan ambil alih diturunkan server saat dibaca** (`status_permintaan`, dari `keadaanPermintaan`: menunggu, ditolak, dijalankan, kedaluwarsa, sesi_berakhir). Status yang tersimpan di dokumen tetap "menunggu" sesudah permintaannya kedaluwarsa atau sesinya berakhir, karena kedua keadaan itu tak pernah ditulis; layar yang membacanya akan menampilkan permintaan basi berjam-jam. Tenggang waktunya tidak disalin ke frontend.

### Yang dibuka kembali dari ADR 0091

[[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]] §Consequences mencatat bahwa leader tak punya riwayat per sesi seluruh tim di web. Keputusan ini **membuka kembali bagian baca** itu (sesi berjalan dan riwayat per sesi), dan menambah Live Support sebagai pembaca. **Bagian tulis tetap dicabut**: izin frontend `marketing.sesi-live.work`, dialog Mulai, dan tombol Ambil alih web tidak kembali. Izin menu yang baru bernama `marketing.sesi-live.view`.

## Consequences

### Yang membaik

- Leader kembali bisa menjelaskan apa yang terjadi pada satu sesi: siapa yang siaran, kapan dijeda, siapa mengambil alih, dan kenapa ditutup, tanpa membuka database.
- Live Support punya layar untuk melihat sesi di tokonya, termasuk sesi yang tak mencatat dirinya sebagai pendukung.
- Sesi yang menggantung melewati batas shift terlihat di satu tempat beserta jam penutupannya.

### Yang memburuk atau tetap terbuka

- ⚠️ **Sesi yang hostnya sudah pulang bisa tampil berjalan paling lama 10 menit** (keputusan 7). Lencana "lewat batas shift" hanya menyala untuk sesi yang punya jam shift; sesi luar shift yang hostnya sudah absen pulang tak berlencana sampai tik berikutnya.
- ⚠️ **Pemegang `integration: supervisor` yang bukan orang marketing ikut melihat seluruh sesi beserta angka.** Bukan pelebaran baru: predikat yang sama sudah membuka riwayat `/live-shifts` dan performa host untuk mereka. Terukur PROD 2026-09-15 sembilan dari 17 pemegang predikat leader lolos hanya lewat peran itu (lihat `isPemimpinBrand` di erp-frontend).
- ⚠️ **Departemen Live Support dicocokkan persis dengan `department_shops.department`.** Nama departemen yang berbeda ejaan membuat layarnya berbunyi "departemen belum punya toko terpetakan" padahal tokonya ada; perilaku sama dengan setoran karya dan KPI Host Live.
- **Titik putus yang diketahui**: sesi perlu koreksi tetap dibetulkan lewat skrip DB (layar hanya menjelaskan artinya), dan Live Support yang belum dicatat pada sesi berjalan tak bisa ditambahkan dari web.
- **Riwayat 92 hari untuk leader membaca `mart_live_sessions` rentang yang sama**; rentang panjang bisa mendekati batas gateway 30 detik seperti riwayat lama. Bawaan layar 7 hari.
- **Tab Sedang Berjalan untuk leader membaca `mart_live_sessions` sejak sesi berjalan PALING AWAL dikurangi 12 jam.** Sesi yang menggantung berhari-hari (host luar shift yang tak pernah absen pulang; tutup otomatis tak punya batas umur sesi) memanjangkan pembacaan itu di setiap pembaruan 60 detik.

### Yang sengaja tidak dilakukan

- **Aksi tulis di web** (ADR 0091, keputusan 2026-08-30).
- **Tautan rincian yang bisa dibagikan** dan rute baca satu sesi (keputusan 8).
- **Rincian per sesi TikTok** yang dijodohkan (keputusan 6).
- **Host membuka menu ini** (sudah punya riwayatnya di MyBharata).
- **Parameter `shop_id`/`host` di rute riwayat** (keputusan 9).

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] § Monitoring sesi live · [[API - Marketing Analytics Service]] § Monitoring sesi live
- [[APP - Web ERP]] § induk Live Support
- [[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]] · [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] · [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] · [[ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift]] · [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]]

# ADR - 0158 Scan Retur Gudang Dijaga Satu Kali dan Selaras dengan Pembukuan, Koreksi Bertahap

> **Status**: 🟢 **Diterima**, 2026-10-08, oleh bagusizzanm (IT). ✅ **Tahap pagar (D1–D5) kodenya sudah merged ke `main` 2026-10-08** (bip-erp#2809, erp-frontend#2194) dan **sudah deploy prod 2026-10-08** (FE sekitar 14:06 WIB, BE 14:29 WIB; keduanya terverifikasi di prod); tahap koreksi (D6) belum ada, dan selama itu IT membetulkan dokumen satu per satu lewat konfirmasi gudang (20 sampai 22 Oktober 2026 untuk lima order; lihat bagian "Pelaksanaan koreksi manual dan pengukuran 20 Oktober 2026"). ⚠️ Pagar **belum terbukti rapat**: tiga order lolos setelah pagar aktif dan penyebabnya belum terbukti. Berdiri di atas pengukuran langsung produksi 2026-10-08 dan pembacaan kode lokal; mengamandemen satu butir [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] (Decision #9, ✅ Implemented) dan menjalankan prinsip yang baru ditulis di [[ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu, Lalu Konfirmasi Massal Hanya untuk Baris Cocok]] §5 (🟡 Diusulkan). Tahap pagar (D1–D5) boleh dibangun. Tahap koreksi (D6) **belum boleh dibangun** sebelum butir di bagian "Belum diputuskan" dan tinjauan kewenangan Proposal terjawab; keputusan tanggal dokumen koreksi sudah ada (lihat bagian "Sudah diputuskan").

## Untuk Manajemen

**Apa yang berubah di layar.** Tombol Simpan pada form retur gudang terkunci selama proses penyimpanan, sehingga satu paket tidak lagi tercatat dua kali karena klik ganda. Bila jumlah yang diisi kurang dari klaim marketplace, petugas harus mengonfirmasi dulu dan melihat barang mana yang kurang. Bila sebuah paket baru sebagian tercatat, form menampilkan barang yang sudah masuk sebagai keterangan dan hanya menawarkan sisanya. Bila satu barang gagal tersimpan di tengah, barang itu tetap ada di form, tidak lenyap. Sistem juga menolak pencatatan yang melebihi jumlah yang diklaim marketplace, walau diisi lewat dua kali simpan.

**Siapa yang terdampak.** Petugas gudang yang mencatat retur (termasuk gudang Sadewa), IT yang sekarang membetulkan selisih dengan skrip manual, dan finance yang menerima dokumen Retur Penjualan. Departemen lain tidak terdampak.

**Apa yang TIDAK dijanjikan.** Tidak ada koreksi sendiri oleh petugas gudang di tahap ini: kesalahan yang sudah tersimpan (SKU salah, jumlah salah) masih harus lewat IT sampai tahap koreksi dibangun, dan tahap itu menunggu dua keputusan. Tidak ada penilaian otomatis atas kondisi barang dan tidak ada AI. Sistem tidak menjamin dokumen Accurate benar bila gudang salah scan; ia hanya memperkecil peluang salah catat dan menjaga stok gudang selalu sama dengan yang dikirim ke pembukuan.

**Perkiraan besaran kerja.** Tahap pertama (pagar) berukuran sedang di dua tempat, layar dan layanan gudang, sekitar dua pekerjaan terpisah. Tahap koreksi berukuran sedang sampai besar karena menyentuh tiga tempat termasuk pembukuan, dan hanya dikerjakan setelah keputusan tanggal dokumen dan kewenangan terjawab.

## Deskripsi

*Selama 60 hari terakhir, 2,1% order retur tercatat dua kali di gudang, hampir semuanya karena simpan ganda dalam hitungan detik, dan tiga perempat di antaranya meninggalkan stok gudang lebih besar daripada yang dipegang pembukuan. Keputusan ini memasang pagar di form dan di layanan gudang supaya satu retur fisik hanya menambah stok satu kali, memastikan jumlah yang dikirim ke pembukuan selalu sama dengan jumlah stok gudang, dan menunda jalur koreksi sampai tanggal dokumen dan kewenangan diputuskan.*

- **Path di repo**: `erp-frontend/src/features/manufacture/components/GudangBarangJadiView.tsx` · `erp-frontend/src/features/manufacture/utils/` (fungsi murni **baru**) · `erp-frontend/src/i18n/locales/id.ts` + `en.ts` · `bip-erp/services/manufacture/transaksi.go` · `bip-erp/services/manufacture/retur_konfirmasi.go` · tahap koreksi saja: `bip-erp/services/manufacture/proposal.go` + `bip-erp/services/integration/internal/usecase/accurate_rts_usecase.go`
- **Tanggal**: 2026-10-08
- **Terkait**: [[Microservices - Manufacture Service]] · [[Workspace/ANALISA - Pengaman Scan Retur Gudang]]

## Context

### Insiden pemicu

Pada 2026-10-07 empat retur (dua Shopee, dua TikTok) berakhir dengan dokumen Retur Penjualan Accurate yang tidak sesuai order. Satu dokumen kelebihan Rp108.000 beserta stok palsu di Accurate, satu dokumen paket isi 2 hanya terbukukan setengah, dua dokumen kehilangan satu komponen paket. Stok gudang bertambah dobel setelah gudang mengulang scan (perkiraan: PJG-002 +4, PJG-004 +2, PJG-008 +2, PJB-002 +1). Perbaikannya dikerjakan IT lewat skrip manual: cadangan baris, ubah jumlah scan di baris AutoSync, lalu Retry.

### Pengukuran produksi 2026-10-08 (baca-saja, 60 hari terakhir)

| Ukuran | Hasil |
|---|---|
| Transaksi retur tertaut | 14.943 |
| (order, SKU) dengan lebih dari satu transaksi | 305, pada 242 dari 11.690 order (2,1%) |
| Selang antar transaksi berurutan (319 pasangan) | ≤60 detik: 246 · 1–10 menit: 50 · 10 menit–1 jam: 5 · 1 jam–1 hari: 1 · >1 hari: 17 |
| Penginput sama / `ref` identik | 318 dari 319 / 308 dari 319 |
| Dibandingkan dengan jumlah di AutoSync (292 pasangan yang bisa dicocokkan) | 209 hanya memegang transaksi terakhir (stok gudang lebih besar), 82 sama dengan total gudang, 1 lain |
| Jumlah scan lawan klaim, SKU tunggal (221 order) | pas 112 · kurang 0 · lebih 8 · tak discan 12 |

Kesimpulan yang boleh ditarik: penyebab dominan adalah **simpan ganda dalam hitungan detik oleh orang yang sama**, bukan scan ulang berhari-hari (17 pasangan, termasuk empat order insiden). Kekurangan jumlah pada SKU tunggal tidak ditemukan; kasus kurang yang terlihat semuanya komponen paket atau paket "isi 2"; frekuensinya untuk paket diukur kemudian (bagian "Pengukuran T4" di bawah). Jalur persis yang meloloskan scan ulang empat order insiden, padahal form menolak membuka order yang sudah punya catatan, **belum teridentifikasi**.

### Pengukuran T4 (2026-10-08, order yang discan sejak 1 September 2026 00:00 WIB)

Baca-saja ke produksi. Populasi: 6.982 order yang punya sedikitnya satu scan retur tertaut; 6.977 dianalisis (5 tanpa rincian klaim dikeluarkan). Klaim per komponen = jumlah retur per SKU listing × `qty_per_unit` pemetaan integration (dedup per master, seperti jalur pembukuan). Sekitar 98% populasi adalah order batal pasca-kirim (klaim disintesis dari seluruh qty order), 142 adalah retur marketplace nyata, dan hanya 3 bertanda parsial.

| Kelompok | Order | Pas | Jumlah kurang | Komponen tak discan | Lebih |
|---|---|---|---|---|---|
| Semua | 6.977 | 98,2% | 7 (0,1%) | 34 (0,5%) | 85 (1,2%) |
| SKU tunggal | 5.199 | 98,5% | 1 | 18 | 55 |
| Paket | 1.778 | 97,2% | 6 (0,3%) | 16 (0,9%) | 30 (1,7%) |
| Paket, batal pasca-kirim | 1.716 | 98,0% | 4 | 7 | 25 |
| Paket, retur marketplace | 62 | 75,8% | 2 (3,2%) | 9 (14,5%) | 5 (8,1%) |

Yang terbaca:
- **Kurang atau tak discan: 41 order (0,6%); paket 22 (1,2%).** Terkonsentrasi pada retur marketplace nyata (20 dari 142, 14%), bukan pada order batal (0,2–0,6%).
- **21 dari 34 "tak discan" bersamaan dengan SKU scan yang tak ada di klaim** (indikasi barang berbeda atau salah SKU, 0,3% order); 13 sisanya komponen yang betul-betul belum atau tidak discan.
- **"Lebih" hampir seluruhnya simpan ganda:** 83 dari 85 order "lebih" punya lebih dari satu transaksi, dan 83 dari 86 order bersimpan ganda berakhir "lebih". Ini memperkuat D1.
- **Pemetaan paket sama di dua sisi:** dari 32 listing paket yang muncul, pemetaan integration dan manufacture identik semua; risiko "pemetaan basi menolak scan sah" di D3 rendah hari ini.

Batas pengukuran: "tak discan" adalah keadaan pada saat ukur dan tidak membedakan "belum sempat discan susulan" dari "memang tidak balik"; hanya order yang sudah punya scan yang terukur (order yang barangnya belum datang tidak ikut); "kurang jumlah" hanya 7 order sehingga persentasenya kasar; ambang keputusan (di bawah sekitar 2% = D2 tetap) adalah usulan yang saya tetapkan sebelum melihat angka dan belum ditegaskan pemutus.

Kesimpulan untuk D2: **tetap**. Frekuensinya rendah (paket non-parsial 1,2%) sehingga konfirmasi jarang muncul, retur parsial praktis tidak ada (3 order) sehingga dialog tidak bertabrakan dengan kasus sah, dan kurang terkonsentrasi pada retur marketplace nyata, tempat konfirmasi paling berguna. Temuan yang tidak tertutup oleh D2 versi awal dan D3: SKU scan di luar klaim, kini diputuskan di D2 (konfirmasi keras, server tidak menolak).

### Yang sudah ada

- Keputusan lama yang diamandemen: [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] Decision #9 memutuskan total per baris tak boleh melebihi klaim marketplace (diblokir) dan jumlah kurang hanya disorot sebagai "parsial sah". Alasan parsial sah tetap berlaku (pelanggan memang bisa mengembalikan sebagian); yang berubah di sini hanya bahwa kurang tidak boleh lolos **diam-diam**.
- Form sudah mengisi barang dari klaim marketplace dan memecah paket jadi komponen; ada peringatan "kurang" dan "lebih" per baris. Tombol Simpan tidak punya penjaga "sedang menyimpan", dan bila satu baris gagal di tengah simpanan berurutan, form menutup dengan pesan sukses yang hanya menghitung yang berhasil sementara baris yang gagal hilang. Form penerimaan surat jalan di layar yang sama sudah punya pola yang benar (baris gagal dipertahankan).
- Layanan gudang menjumlahkan stok per transaksi dan tidak punya pemeriksaan batas atas jumlah per (order, SKU); permintaan dengan `ref` identik diterima berulang.
- Pembukuan **mengganti** jumlah per (order, SKU) dengan konfirmasi terakhir, membuang baris berjumlah nol, dan setiap konfirmasi gudang menghapus lalu membuat ulang dokumen Accurate (nomor sama, tanggal mengikuti scan terbaru). Konfirmasi gudang mengirim jumlah **satu transaksi**, bukan jumlah kumulatif. Sapuan dan kirim-ulang hanya menilai per nama SKU, jadi koreksi jumlah untuk SKU yang sudah tercatat tidak pernah terkirim.
- Layanan gudang sudah menyimpan definisi paket ke komponen (salinan dari data HPP) sehingga jumlah klaim per komponen bisa dihitung di sisi server, dengan catatan salinannya bisa tertinggal dari sumbernya. Backend juga sudah mengirim ke layar daftar SKU yang tercatat dan daftar komponen yang belum discan, tetapi layar belum membacanya.
- Ledger gudang tidak punya jalur hapus; satu-satunya jalur koreksi jumlah adalah **Proposal koreksi**, yang mengubah jumlah transaksi dan stok secara atomik dengan persetujuan dua tahap dan kunci periode, tetapi tidak memeriksa apakah transaksinya retur dan tidak memberi tahu pembukuan. Artinya koreksi lewat jalur itu hari ini membuat stok gudang dan pembukuan berselisih tanpa satu pun tanda.

### Yang ditolak sejak awal

- Tipe transaksi koreksi baru (pengurang stok bertanda koreksi) sebagai jalur koreksi: konfirmasi retur tidak memeriksa tipe transaksi sehingga transaksi keluar yang membawa kunci retur ikut dikonfirmasi, dan transaksi bermarka tertentu bisa didorong ke Accurate sebagai penyesuaian persediaan. Risiko dobel pembukuan lebih besar daripada manfaatnya.
- AI atau penilaian otomatis: sama seperti ADR 0124 §6.

## Decision

### D1. Satu retur fisik, satu pencatatan

Tombol Simpan form retur terkunci selama proses penyimpanan berjalan, dan sisi server memperlakukan permintaan yang mengulang kunci referensi transaksi retur tertaut yang sama sebagai sudah tercatat, bukan sebagai tambahan. Ini menutup penyebab dominan terukur (77% pasangan ganda berselang ≤60 detik).

### D2. Jumlah kurang dari klaim wajib dikonfirmasi, bukan diblokir

Mengamandemen ADR 0025 Decision #9. Jumlah **lebih** dari klaim tetap diblokir. Jumlah **kurang** kini membuka konfirmasi yang menyebut tiap barang dan selisihnya; petugas memilih kembali melengkapi atau tetap menyimpan karena barang memang tidak ikut kembali. Alasan kekurangan **tidak disimpan** di tahap ini. Baris tanpa jumlah tidak lagi dibuang diam-diam: ia dihitung sebagai kurang.

**SKU yang discan tetapi tidak ada di klaim order** (diputuskan bagusizzanm, 2026-10-08): diizinkan dengan **konfirmasi keras**, tidak ditolak. Konfirmasinya menyebut SKU itu tidak ada di klaim order ini dan bahwa pembukuan menolak membukukan SKU yang tidak pernah dibeli pesanan tersebut, sehingga stok gudang bertambah sementara dokumen retur tertahan. Server tidak membatasi SKU berklaim nol, karena data klaim tidak membedakan "tidak pernah dibeli" dari "dibeli tetapi tidak diretur" (yang kedua sah, mis. koreksi). Dasarnya pengukuran T4: 26 order (0,4%) sejak 1 September punya scan di luar klaim; dari 25 yang ditemukan di pembukuan, 3 tertahan di gerbang SKU asing, 22 sudah terbukukan dan 18 dari itu sudah dikoreksi manual (`[KOREKSI-SCAN]`). Pembukuan tetap menjadi penjaga terakhir; gerbangnya tidak diubah di sini.

### D3. Batas kumulatif per (order, SKU), dijaga di server

Total jumlah (reuse + rework + reject) seluruh transaksi retur tertaut untuk satu (order, SKU) tidak boleh melebihi jumlah klaim marketplace untuk komponen itu. Pemeriksaan ada di layanan gudang, bukan hanya di form. Permintaan yang melanggar ditolak dan **tidak mengubah apa pun**, termasuk stok. Klaim per komponen dihitung dari klaim per SKU listing dikali isi paket. Bila SKU tidak dikenal oleh pemetaan, pemeriksaan tidak menolak (arah aman: tidak menghalangi retur yang sah karena data pemetaan basi). Hal yang sama untuk SKU berklaim nol: server tidak menolak, konfirmasinya ada di form (lihat D2).

### D4. Pembukuan menerima jumlah kumulatif

Konfirmasi gudang untuk (order, SKU) membawa **jumlah kumulatif** seluruh transaksi tertaut untuk (order, SKU) itu, bukan jumlah transaksi terakhir. Dengan itu stok gudang dan jumlah yang dipegang pembukuan selalu sama tanpa mengubah semantik "ganti" di sisi pembukuan.

### D5. Form menawarkan hanya yang belum tercatat

Untuk paket yang sebagian sudah tercatat, form menampilkan SKU yang sudah tercatat sebagai keterangan (bukan baris isian) dan hanya menawarkan sisanya, memakai daftar yang sudah dikirim backend. Bila satu baris gagal di tengah simpanan berurutan, baris itu tetap di form dan petugas melihat barang mana yang gagal. Batas yang disengaja: SKU yang sudah tercatat tetapi jumlahnya salah **tidak** bisa dibetulkan dari form; itu urusan D6.

### D6. Koreksi dibangun bertahap, lewat Proposal koreksi yang sudah ada

Setelah pagar D1–D5 hidup, koreksi jumlah untuk transaksi retur tertaut dibangun dengan **memperluas Proposal koreksi**: setelah disetujui, jumlah kumulatif yang baru diteruskan ke pembukuan dalam langkah yang sama, supaya stok gudang dan pembukuan tidak berselisih. Ini sekaligus menutup selisih diam-diam yang sudah ada hari ini pada jalur itu. **Belum boleh dibangun** sampai dua hal terjawab: (a) tanggal dokumen saat koreksi, **sudah diputuskan: mengikuti tanggal koreksi** (lihat bagian "Sudah diputuskan"), (b) pembukuan menerima koreksi ke nol, (c) kewenangan persetujuan koreksi gudang dan pemeriksaan gerbang persetujuan jalur itu, yang dikerjakan sebagai pekerjaan terpisah di repo kode.

### D7. Prosedur manusia selama koreksi belum ada

Sampai D6 hidup, urutannya: gudang memeriksa fisik dulu; menginput **hanya SKU yang belum tercatat** dan jangan scan ulang yang sudah; bila ada SKU salah atau jumlah salah, lapor IT untuk dibetulkan di sistem dan stok yang kelebihan dikoreksi terpisah; bila finance terpaksa mengedit dokumen Retur Penjualan di Accurate lebih dulu, finance **wajib mengabari IT pada hari yang sama** supaya catatan sistem disamakan, karena membangun ulang dokumen (Retry, konfirmasi baru) menghapus dan menimpa hasil edit manual. Tombol penanda manual tidak berlaku untuk retur yang sudah dibukukan sistem.

### D8. Yang tidak diputuskan di sini

Mengubah semantik "ganti" pembukuan, mengubah arti tiga kondisi (Reuse, Rework, Reject), mengubah gerbang konfirmasi gudang ADR 0025, dan menyentuh konfirmasi massal ADR 0124. Mengukur frekuensi jumlah kurang untuk komponen paket adalah pekerjaan terpisah dan tidak menahan D1–D5.

## Sudah diputuskan setelah ADR ini diusulkan

**Tanggal dokumen saat koreksi mengikuti tanggal koreksinya, bukan tanggal scan awal** (bagusizzanm, 2026-10-08). Alasannya: perubahan harus terlacak di pembukuan; dokumen yang tanggalnya tetap di tanggal scan awal menyembunyikan bahwa ada koreksi. Ini sejalan dengan perilaku yang sudah ada (tanggal dokumen mengikuti scan terbaru). Konsekuensi yang diterima sadar: koreksi atas retur yang sudah dibukukan di bulan lalu memindahkan pembalikan penjualannya ke periode koreksi (terlihat pada insiden 7 Okt: tiga dokumen berpindah dari 26 Sep, 12 Sep, dan 30 Sep ke 7 Okt), dan dokumen yang bulan bukunya sudah lewat batas sync toko bisa ditahan gerbang bulan buku, itu ranah finance. Finance perlu diberi tahu aturan ini sebelum tahap koreksi dibangun; ia tidak lagi menahan pembangunan.

**Pengecualian: dokumen pengganti tetap bertanggal fisik barang tiba bila periodenya masih terbuka** (jawaban finance 2026-10-15, diteruskan oleh IT). Untuk order `585279137460029417` (dokumen `RTR/2026/08/07/242-KY+GB` bertanggal 7 Agustus), finance memilih dokumen pengganti **tetap bertanggal Agustus**, dan menyatakan periode Agustus masih bisa direvisi. Alasan finance: barangnya tiba di Agustus, jadi dokumen bertanggal Oktober membuat stok Agustus dan September kurang dan stok Oktober lebih. Ini mengecualikan aturan "tanggal koreksi mengikuti tanggal koreksi" di atas, berlaku hanya bila periodenya masih terbuka dan finance menyetujuinya per kasus; bila periodenya terkunci, Accurate menolak menghapus dokumen lama dan pembangunan ulang berhenti dengan galat. Untuk order yang barang fisiknya berbeda dari faktur, finance memilih **dokumen mengikuti faktur** (cara 2), dan selisih fisiknya dijurnal sendiri lewat Penyesuaian Persediaan di Accurate, bukan dicatat sebagai keterangan.

## Pelaksanaan koreksi manual dan pengukuran 20 Oktober 2026

Selama D6 belum dibangun, koreksi dikerjakan IT satu per satu. Bagian ini mencatat jalur yang terbukti jalan dan apa yang diukur; angka dan nomor bertanggal, ukur ulang sebelum dipakai.

**Jalur koreksi dokumen yang sudah dibukukan** (dibaca di `bip-erp` `origin/main` `3a8271ef9`, 2026-10-23; nomor baris bergeser tiap merge, cari lewat nama fungsi):

- Dokumen SENT dikoreksi dengan **mengirim ulang konfirmasi gudang** (`POST /accurate/daily-returns/warehouse-confirm`) berisi jumlah yang benar per (order, SKU) dan `scan_date`. Konfirmasi **mengganti** jumlah per (order, SKU) (`mergeWarehouseItems`, `accurate_rts_usecase.go:4397`), tanggal dokumen diambil dari `scan_date` item dan bukan dari hari konfirmasi diproses (`scanDateFromItems`, `:4417`), lalu dokumen dibangun ulang (`rebuildAndSendGroup`) dengan **nomor RTR yang sama** dan tanggal yang tersimpan di baris (`:6182`, `:6214`), yaitu dihapus lalu dibuat bila isinya berubah (`:6291`). Mengisi `scan_date` dengan tanggal fisik barang tiba menjaga dokumen tetap di tanggal itu.
- `RetryDailyReturn` untuk baris yang sudah SENT **langsung keluar tanpa berbuat apa-apa** (`:7298`): Retry bukan jalur koreksi dokumen SENT. Baris FAILED (mis. "melebihi qty terjual di faktur") dikoreksi dengan konfirmasi yang sama, dan hasilnya dokumen baru bernomor baru.
- Yang **tidak** dipakai: menyunting `warehouse_items` langsung di database, dan konfirmasi tanpa `scan_date` (tanggal dokumen jatuh ke hari konfirmasi, melanggar keputusan finance di atas).

**Yang dijalankan** (skrip sekali pakai milik IT, dry-run bawaan, cadangan baris sebelum diubah, tidak masuk repo): lima order, 20 dan 22 Oktober 2026.

| Order | Dokumen | Perubahan |
|---|---|---|
| `585867761144006565` | `RTR/2026/10/09/167-BH` | PJB-002 dari 2 menjadi 1, Rp189.000 menjadi Rp94.500 |
| `586016295544259817` | `RTR/2026/10/02/091-BH` | sama |
| `585879810814215442` | baris FAILED menjadi dokumen baru `RTR/2026/10/09/181-BH` | PJB-002 ×1, tanggal 9 Okt |
| `585279137460029417` | `RTR/2026/08/07/242-KY+GB` | PJG-002 1 reuse + 1 rework, PJG-004 2 reuse; tanggal 7 Agu tetap, Rp98.000 menjadi Rp196.000 |
| `586201339375748436` | `RTR/2026/10/03/093-KY+GB` | mengikuti faktur: PJG-002 ×1 + PJG-004 ×1 |

Finance memeriksa dua yang pertama di Accurate dan cocok; pemeriksaan tiga lainnya belum tercatat di sini. Stok WMS untuk transaksi yang jumlahnya lebih belum ikut dikoreksi oleh skrip ini: itu urusan Proposal koreksi (di bawah).

**Pengukuran 2026-10-20 (baca-saja, prod):** dari 3.972 transaksi retur tertaut sejak 8 Oktober, 3.958 pasangan (order, SKU) bisa dinilai terhadap klaim marketplace (item retur, atau item order untuk order batal, dipecah ke komponen lewat pemetaan); **enam pasangan di empat order melebihi klaim** dan ada **empat ref kembar**. Pengelompokannya:

- 8 Okt 11:08 WIB (satu order, tiga SKU): tiap SKU tersimpan dua kali dalam 0 sampai 3 detik, **tiga jam sebelum** backend pagar naik (14:29 WIB). Penyebabnya pagar belum ada.
- 9 Okt, gudang Sadewa (dua order): **satu** transaksi berjumlah 2 padahal klaim terbaca 1 di integration, **sesudah** pagar aktif. Penyebab **belum terbukti**.
- 15 dan 17 Okt, gudang Tinggar (satu order, PJB-006): ref yang sama tersimpan dua kali selang dua hari (reject 1 dan 1, klaim 1), padahal seharusnya dijawab "sudah tercatat". Penyebab **belum terbukti**.
- Satu order lagi (2 Okt, jumlah 2 untuk klaim 1) terjadi sebelum pagar.

Dua dugaan yang belum dibuktikan untuk dua kelompok terakhir: klaim gagal terambil saat itu (pagar sengaja terbuka bila klaim tak terbaca, dan hanya mencatat peringatan di log container), atau pemetaan SKU gagal terbaca. Log container hilang tiap deploy, jadi keputusan pagar tidak bisa dibuktikan sesudah kejadian. Usulan yang belum dikerjakan: menyimpan keputusan pagar (diterima, sudah tercatat, ditolak, klaim tak terambil) ke database per simpan.

**Proposal koreksi di layar** (dibaca di `erp-frontend` `origin/main`, 2026-10-22), karena jalurnya tak ketemu bagi yang mencarinya:

- Diajukan dari menu **Riwayat Aktivitas** (`/manufacture/history`, tab Ledger Transaksi, tombol "Koreksi Input"), disetujui di **Persetujuan & Akses Akun** (`/manufacture/approvals`, PPIC lalu SPV). Kedua tab diberi daftar peran **kosong** (`akses.ts:55-56`), artinya hanya PPIC dan SPV yang melihatnya.
- Layar **menolak jumlah nol atau kurang** (`HistoryView.tsx:110`), jadi koreksi ke nol tidak bisa diajukan; itu bagian butir "Koreksi ke nol" di bawah.
- Koreksi hanya mengubah `qty` transaksi dan stok (`proposal.go:154`); rincian kondisi (reuse, rework, reject) **tidak ikut berubah**, sehingga laporan yang membaca rincian kondisi masih menampilkan jumlah lama dan kirim-ulang konfirmasi bisa mengirim angka lama.
- Tombol Koreksi hanya muncul untuk transaksi bulan berjalan, kecuali pengaju punya izin edit (`period-lock.ts`).
- Pencarian ledger mencocokkan nomor resi dan nomor order retur sejak erp-frontend PR #2664 (merged 2026-10-21; status deploy prod belum diukur). Sebelumnya hanya SKU, nama barang, No. Dokumen, dan supplier/customer, padahal gudang bekerja dari scan resi.

## Belum diputuskan

1. **Koreksi ke nol.** Pembukuan membuang baris berjumlah nol, sehingga membuang satu SKU dari dokumen tidak bisa diungkapkan lewat jalur yang ada. Perlu aturan eksplisit sebelum D6. Layar Proposal koreksi juga sudah menolak jumlah nol atau kurang, jadi aturannya menyangkut dua tempat (layar dan pembukuan).
(Butir "SKU yang discan tetapi tidak ada di klaim order" sudah diputuskan, lihat D2.)

## Consequences

**Yang didapat**

- Penyebab dominan selisih (simpan ganda) tertutup dengan pagar murah di dua tempat.
- Stok gudang dan pembukuan tidak lagi berselisih diam-diam pada jalur normal (D4).
- Kegagalan simpan di tengah tidak lagi menghilangkan barang dari form.
- Selisih laten pada jalur Proposal koreksi dikenali dan dijadwalkan untuk ditutup (D6).

**Yang dibayar**

- ⚠️ Setiap teks baru di layar ini wajib lewat `react-i18next` dengan kunci di `id.ts` **dan** `en.ts` ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]). Layar warisan ini hampir seluruhnya belum ber-i18n, jadi tiap teks yang tersentuh menambah kerja yang tidak terlihat dari besar perubahannya.
- Layar warisan tanpa uji untuk logika form: perubahan harus memisahkan fungsi murni lebih dulu supaya bisa diuji, dengan kontrol negatif.
- D3 bergantung pada salinan pemetaan paket di layanan gudang; salinan yang basi bisa menolak scan sah. Itu sebabnya SKU tak dikenal tidak ditolak, dan pesan penolakan harus menyebut klaim dan jumlah tercatat supaya petugas bisa melapor.
- Alur persetujuan dua tahap pada koreksi menambah beban untuk urusan gudang; kewenangannya diputuskan sebelum D6.

**Batas yang sengaja tidak dilewati**

Tidak mengubah integration pada tahap pagar (D1–D5), tidak menambah jalur edit atau batal di form, dan tidak menyentuh data produksi.

**Konsekuensi deploy**

Tahap pagar tidak butuh env baru dan tidak butuh kategori inbox baru. Urutan: layanan gudang (backend) lebih dulu, layar menyusul; layar aman bila batas server belum ada, karena yang ditambah di layar hanya pencegahan. Tahap koreksi menambah perubahan di pembukuan, sehingga urutannya pembukuan, layanan gudang, lalu layar, dan tiap koreksi menghapus dan membuat ulang dokumen Accurate.

## Dokumen Terkait

- [[Microservices - Manufacture Service]] · [[Microservices - Integration Service]]
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] · [[ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu, Lalu Konfirmasi Massal Hanya untuk Baris Cocok]] · [[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]] · [[ADR - 0144 Retur yang Sudah Dibukukan Manual oleh Finance Ditandai per Order dan Dihormati Semua Jalur Auto-Sync]]
- Papan kerja: [[Workspace/ANALISA - Pengaman Scan Retur Gudang]]

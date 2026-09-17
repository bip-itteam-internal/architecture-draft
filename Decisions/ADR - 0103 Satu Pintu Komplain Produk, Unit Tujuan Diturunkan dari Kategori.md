> **Status**: 🟡 **Diusulkan** 2026-09-17, disetujui pemilik proses (opsi A). **Keputusan 2 sisi register gudang (T9) merged 2026-09-17** (bip-erp #1957, erp-frontend #1634), terverifikasi DEV lewat gateway dan bundel frontend, **belum PROD**. **Keputusan 7 bagian `ditolak` (T10) merged 2026-09-17** (bip-erp #1965, erp-frontend #1641), terverifikasi DEV lewat gateway, **belum PROD**; bagian `dialihkan` menunggu T13. Keputusan lain belum ada kodenya. Menggantikan **keputusan 2** [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] (pengaju memilih tujuan lebih dulu) dan memicu keputusan 12-nya. Keputusan lain ADR 0099 tetap berlaku.

## Untuk Manajemen

- **Yang berubah di layar**: semua keluhan produk diajukan lewat SATU formulir, baik dari baris ulasan marketplace maupun tanpa ulasan. Pengaju cukup memilih jenis keluhannya; unit yang akan menangani tampil sendiri dan tidak bisa diubah pengaju. Nama produk dan SKU diisi sistem dari pesanannya, jadi pengaju hanya menulis cerita keluhan dan melampirkan foto. Formulir lama "Komplain ke QC" diganti formulir ini. Bila jenis keluhannya ternyata keliru, unit penerima menekan "Ganti kategori" dan komplain pindah sendiri ke unit yang benar, pengaju dikabari. Keluhan yang tidak cocok dengan jenis mana pun diteruskan ke supervisor brand pemilik toko untuk dipilah. Komplain gudang yang ditolak tidak lagi menurunkan skor packer.
- **Siapa terdampak**: pemegang toko dan staf marketing Kyura dan Beauty Hacks (pengaju), SPV Kyura dan SPV Beauty Hacks (memilah keluhan "Lainnya"), tim gudang packing (aturan skor KPI berubah), staf QC (mendapat daftar jenis keluhan dan kini menentukan tingkat keparahan sendiri).
- **Tidak dijanjikan**:
  - Nomor batch dan tanggal kedaluwarsa **tidak** terisi otomatis. Keduanya tidak tercatat di data pesanan mana pun, jadi tetap dibaca dari foto kemasan.
  - Pesanan yang tidak ada di data sistem tidak bisa diajukan. Diukur atas ulasan buruk yang ada: 4 dari 65 untuk jalur QC, dan 20 dari 65 untuk jenis keluhan gudang karena data gudang baru ada sejak Juli 2026.
  - Tidak tersambung otomatis ke CAPA.
  - Pengaju tetap melihat nasib komplainnya di dua halaman, gudang dan QC.
  - Tetap hanya Shopee, dan keluhan untuk ekspedisi atau vendor tetap belum punya tempat.
- **Besaran kerja**: sedang. Enam task, menyentuh warehouse-service, employee-service, notification-service, dan web ERP. Bagian QC menunggu tim QC menetapkan daftar jenis keluhannya; bagian gudang bisa berjalan lebih dulu.

## Deskripsi

*Satu pintu pengajuan untuk semua komplain produk. Pengaju memilih kategori, bukan unit; unit tujuan diturunkan dari register mana yang memiliki kategori itu, tanpa tabel pemetaan dan tanpa register ketiga. Produk, SKU, dan pesanan diisi server dari data pesanan. Unit penerima dapat mengalihkan komplain ke unit lain, keluhan tanpa kategori dipilah SPV brand, dan komplain gudang yang ditolak atau dialihkan tidak lagi dihitung ke KPI packer.*

- **Path di repo**:
  - `bip-erp/services/warehouse/komplain.go` (daftar kategori diterbitkan, status `dialihkan`, ganti kategori)
  - `bip-erp/services/warehouse/kpi_komplain.go` (`ditolak` dan `dialihkan` tidak dihitung)
  - `bip-erp/services/warehouse/komplain_alih.go` (**baru**, rute internal menerima dan mengirim komplain yang dialihkan)
  - `bip-erp/services/employee/quality_complaint.go` (kategori tertutup, isian server, `company_id`, race `ReplaceOne`, ganti kategori)
  - `bip-erp/services/employee/quality_complaint_alih.go` (**baru**, pasangan rute internal di sisi QC)
  - `bip-erp/shared-library/models/employee/models.go` (`QualityComplaint`: kategori, identitas item, `company_id`, penanda sumber)
  - `bip-erp/shared-library/models/notification/models.go` + `bip-erp/services/notification/webpush.go` (kategori inbox baru dan aturan rute web)
  - `erp-frontend/src/features/komplain/` (**baru**, formulir satu pintu)
  - `erp-frontend/src/features/integration/reviews/components/ajukan-komplain-modal.tsx` dan `erp-frontend/src/features/quality/complaint/components/complaint-form-modal.tsx` (diganti formulir satu pintu)
  - `erp-frontend/src/features/warehouse/komplain/types.ts` (salinan tangan daftar kategori dihapus)
  - `erp-frontend/src/components/layout/sidebar-menus.tsx`, `erp-frontend/src/features/erp/notification/inbox/kategori.ts`, `src/i18n/locales/{id,en}.ts`
- **Tanggal**: 2026-09-17
- **Terkait**: [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] · [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[Microservices - Warehouse Service]] · [[ANALISA - Komplain dari Ulasan Marketplace]]

## Context

Kebutuhan datang sebagai solusi: "satu pintu untuk semua komplain produk; pengaju tidak memilih departemen karena takut salah, cukup pilih kategori dan otomatis masuk ke departemen terkait", disusul "tanpa isian manual nama produk, SKU, dan lainnya yang rawan salah input". Di baliknya ada dua kebutuhan:

1. **Pengaju tidak dapat diandalkan menentukan unit penanggung jawab.** ADR 0099 keputusan 2 menyuruhnya memilih tujuan lebih dulu. Salah pilih bukan sekadar komplain yang tersesat: di register gudang, komplain yang **ditolak pun tetap menambah** `KomplainPacking`, pembilang KPI baris 1 gudang packing (`services/warehouse/kpi_komplain.go:96-108`, dibaca 2026-09-17 dari `main` sesudah bip-erp #1940). Hanya `KomplainBelumSelesai` yang membedakan status. Jadi keluhan yang salah alamat menurunkan skor packer walau gudang sudah menolaknya.
2. **Isian manual tidak dapat diperiksa.** Formulir komplain QC menerima `product`, `sku`, dan `order_ref` sebagai teks bebas; satu-satunya validasi adalah `title` wajib (`services/employee/quality_complaint.go:73-75`), tanpa pengecekan ke data pesanan atau produk mana pun.

**Terukur di PROD 2026-09-17** (baca saja):

| Yang diukur | Hasil |
|---|---|
| Ulasan bintang 1-3 berteks | 65 (31 Mei 2025 sampai 15 September 2026, seluruhnya Shopee) |
| ...yang membawa `order_sn` dan `item_id` | 65 dari 65. Ulasan **tidak** menyimpan SKU maupun varian |
| ...yang pesanannya ada di `transaction_orders`, item ulasan cocok ke `items[].id` | **61 dari 65**, seluruh 61 ber-SKU dan bernama. 4 pesanan berisi lebih dari satu item, dan item ulasannya tetap tertunjuk tepat |
| ...yang pesanannya ada di `fulfillment_orders` (syarat register gudang) | 45 dari 65. Dokumen fulfillment terlama dibuat 2026-07-12; empat ulasan Agustus sampai September pun tak ditemukan, sebabnya belum diukur |
| `fulfillment_orders` yang item-nya ber-SKU kosong | 28 dari 132.524 |
| Isi `warehouse_komplain_gudang` | 0 |
| Koleksi `quality_*` di `employee_db` | **tidak ada satu pun**. Register komplain QC dan CAPA sama-sama belum pernah terisi di produksi (kontrol positif: 30 koleksi lain terbaca) |
| Nomor batch atau tanggal kedaluwarsa produk jadi di pesanan, fulfillment, atau stok | tidak ada. `LotBahan.TanggalKadaluarsa` hanya untuk bahan baku dan tak tertaut ke SKU jual |

Penggolongan manual atas 65 ulasan yang sama: gudang 11, mutu produk 13 (dugaan tidak asli 4, segel atau kemasan produk terbuka 4, pecah 2, isi kosong 1, mendekati kedaluwarsa 1, isi tak jelas 1), pengiriman 5, tidak sesuai iklan 6, dugaan efek tidak diinginkan 3, tidak mempan 16, netral 11. **Yang dapat ditindak unit yang sudah ada sekitar 24 dalam 15,5 bulan, kira-kira 1,5 per bulan.** Volume ini yang menentukan bobot rancangan di bawah.

**Yang sudah ada dan dipakai sebagai dasar:**

- Dua register dengan pemilik berbeda: `warehouse_komplain_gudang` (warehouse-service) dan `quality_complaint` (employee-service). Keduanya tidak menyimpan `company_id` dan tidak punya jalur pemindahan antar unit.
- Register gudang sudah punya daftar kategori tertutup, tetapi **tidak menerbitkannya**: frontend menyalinnya dengan tangan (`erp-frontend/src/features/warehouse/komplain/types.ts:1-16`, komentarnya menyebut alasan itu).
- Register gudang sudah menyalin atribusi packer dari pesanannya di server, bukan dari body. Pola "diisi server, bukan diketik" sudah terbukti di sana.
- integration-service punya pencarian satu pesanan yang menerima `order_sn` dan mengembalikan `items[]` lengkap (`GET /transactions/orders/:id`). Respons itu juga memuat data pembeli.
- Resolver atasan per departemen sudah ada dan dipakai alur pengajuan lain (`atasanDepartemen`, `services/employee/supervisor_lookup.go:203`; rute `GET /internal/department-approver`).
- Pilihan berkelompok sudah ada di komponen bersama frontend (`components/ui/combobox.tsx`, prop `groups`) dan dipakai tiga fitur.

⚠️ **Koreksi atas ADR 0099.** Tabel register di Context ADR itu menyebut `quality_complaint` "dipakai". Diukur 2026-09-17 koleksinya belum pernah tercipta di PROD.

⚠️ **Dasar regulatif keluhan pelanggan tetap tidak ada di vault.** [[QA - Deviation & CAPA]] masih stub, sumber CAPA tidak memuat keluhan pelanggan, dan kategori dugaan efek tidak diinginkan tetap ditahan (ADR 0099 keputusan 11).

**Tiga opsi yang ditimbang.**

| | A. Satu pintu di layar, register tetap dua (**dipilih**) | B. Register pintu tersendiri | C. Satu register gabungan |
|---|---|---|---|
| Inti | Formulir tunggal; tiap register menerbitkan kategorinya, unit diturunkan dari pemiliknya | Koleksi baru menampung semua komplain lalu meneruskan ke register unit | Gudang dan QC dilebur jadi satu koleksi |
| Kelebihan | Permukaan baru terkecil, tunduk [[ADR - 0002 Database-per-Service]], tanpa tabel pemetaan | Satu daftar bagi pengaju; "Lainnya" punya antrean tercatat | Tanpa migrasi, keduanya nol dokumen |
| Kekurangan | Pengaju tetap melihat dua halaman daftar; pemindahan lintas service butuh idempotensi | Status hidup di dua tempat dan wajib disinkronkan, berat untuk 1,5 per bulan | Kosakata dan wewenang gudang dan QC berbeda, memenuhi kriteria pemisahan [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]]; KPI packer ditulis ulang |

## Decision

1. **Satu pintu untuk semua komplain produk; pengaju memilih KATEGORI, bukan unit.** Kategori ditampilkan berkelompok per unit, dan sesudah dipilih unit tujuannya tampil sebagai keterangan yang tak bisa diubah. Pintu yang sama dipakai dari baris ulasan maupun tanpa ulasan.

2. **Unit tujuan diturunkan dari register yang MEMILIKI kategori itu.** Tidak ada tabel pemetaan kategori ke unit dan tidak ada master kategori pusat: masing-masing register menerbitkan daftar kategori tertutupnya lewat endpoint baca, dan frontend menyusun pintunya dari keduanya. Satu fakta tetap tinggal di satu tempat, dan salinan tangan di frontend dihapus. ADR 0099 keputusan 1 (dua register, tanpa register ketiga) tetap berlaku.
   - *Sisi register gudang (T9, merged 2026-09-17, bip-erp #1957 + erp-frontend #1634, belum PROD):* `GET /wms/komplain/kategori` membalas kode saja, berurutan, tanpa field unit (pemanggil tahu unitnya dari rute yang ia minta). Digerbang **identitas saja**, bukan gerbang baca komplain: kodenya tak rahasia, dan gerbang baca memaksa pemegang toko memanggil integration-service. Label ditulis frontend per kode (`warehouse.komplain.kategoriLabel.<kode>`); kode tanpa terjemahan tampil sebagai kodenya. Rinciannya di [[Microservices - Warehouse Service]].

3. **Register QC mendapat daftar kategori tertutup, dan isinya ditetapkan tim QC.** Usulan awal dari penggolongan ulasan: `dugaan_tidak_asli`, `segel_terbuka`, `isi_tidak_sesuai`, `kedaluwarsa`. **Tingkat keparahan ditentukan QC saat validasi**, bukan ditebak pengaju.

4. **Produk, SKU, dan pesanan diisi SERVER.** Pengaju hanya mengirim nomor pesanan dan identitas item, yang dari baris ulasan sudah terbawa. Register mengambil nama produk dan SKU dari data pesanan integration-service lalu menyalinnya; nilai serupa dari klien diabaikan. Pesanan yang tak ditemukan ditolak dengan pesan yang menjelaskan sebabnya. Tanpa ulasan, pengaju memasukkan nomor pesanan, server mengeceknya, lalu pengaju memilih produk dari isi pesanan itu. Salinan ini bertanggal dan tak berubah bila datanya kelak disunting, prinsip yang sama dengan ADR 0099 keputusan 4.
   - Register gudang tetap per **pesanan**, tidak per item, dan tetap memverifikasi ke `fulfillment_orders` seperti sekarang. Register QC per **item**.
   - ⛔ Data pesanan diambil **server ke server**, tidak lewat layar pengaju, karena memuat data pembeli yang tidak dibutuhkan untuk mengajukan komplain. Endpoint pilih-produk untuk pengaju hanya mengembalikan item.
   - Gerbang tulis register QC mengikuti register gudang: pemegang toko atas tokonya sendiri, atau staf marketing. Ini meneruskan koreksi ADR 0099 bahwa hak mengajukan diturunkan dari kepemilikan toko.

5. **Unit penerima dapat mengganti kategori.** Dalam unit yang sama, kategorinya cukup diubah. Ke unit lain:
   - service asal membuat komplain di register tujuan lewat rute internal berkunci layanan, **idempoten atas id komplain asal** (register tujuan menolak salinan kedua);
   - baru sesudah itu komplain asal ditandai **`dialihkan`**, status akhir yang merujuk komplain tujuan. Bila penandaan gagal, mengulang aman karena langkah pertama idempoten;
   - alasan wajib diisi; pengaju dan unit tujuan dikabari;
   - tidak menunggu persetujuan pengaju.

6. **Keluhan "Lainnya" tidak disimpan di register mana pun.** Formulir mengirim kabar inbox kepada SPV brand pemilik toko, ditemukan lewat resolver atasan yang sudah ada, berisi tautan ke ulasan atau pesanannya. SPV mengajukan ulang lewat pintu yang sama dengan kategori yang benar. Bila tak ada SPV yang ditemukan, pengaju diberi tahu di layar, bukan dibiarkan senyap.

7. **KPI gudang packing: `ditolak` dan `dialihkan` TIDAK dihitung ke `KomplainPacking`.** `ditolak` wajib disertai alasan tindak lanjut; pengaju sudah dikabari saat komplain ditutup (ADR 0099 keputusan 8). Ini perubahan aturan angka penilaian orang, jadi tim gudang diberi tahu sebelum naik ke PROD.
   - *Bagian `ditolak` (T10, merged 2026-09-17, bip-erp #1965, belum PROD):* yang ditolak dikeluarkan dari pembilang, dari cacah per kategori, dan dari cacah per packer. Penolakan tanpa alasan dibalas 400 oleh backend, bukan hanya dicegah layar, karena begitu yang ditolak tak dihitung, penolakan tanpa alasan menjadi jalan menghapus komplain dari penilaian tanpa jejak. Cacah yang ditolak diterbitkan terpisah sebagai `komplain_ditolak` dan ditulis di catatan penilaian, supaya gudang yang menolak semua komplain tetap terlihat; field itu **bukan** komponen akurasi dan tidak boleh dijumlahkan ke `komplain_packing` (kontraknya di [[API - Warehouse Service]]). Skor periode yang sudah tersimpan tidak dihitung ulang.

8. **Formulir `/icc/komplain-qc` diganti pintu tunggal.** Halaman daftar tetap per unit: `/warehouse/komplain` dan `/quality/komplain`.

9. **Tidak disambungkan ke CAPA sekarang.** CAPA belum pernah terisi di PROD, jadi sambungan otomatis akan dibangun di atas modul yang belum dipakai. QC membuat CAPA sendiri bila perlu. Ditinjau ulang begitu CAPA benar-benar dipakai.

10. **ADR 0099 keputusan 5, 6, 7, 9, 10, dan 11 tetap berlaku**: kategori dipilih manusia, tujuan tanpa register tidak dipaksakan, "tidak mempan" tidak menjadi komplain, tanpa SLA, hanya Shopee, dan kategori efek samping ditahan. **Keputusan 12 terpicu**: `company_id` dan race `ReplaceOne` register QC dikerjakan bersama perubahan register itu.

## Consequences

**Yang membaik.** Pengaju tak perlu tahu struktur organisasi, dan keluhan yang salah jenis tidak lagi menghukum packer. Nama produk dan SKU di komplain QC dapat dipercaya karena berasal dari pesanan. Salinan tangan kategori di frontend hilang, sehingga menambah kategori di backend langsung terlihat di pintu.

**Yang memburuk, dan diterima sadar.**
- Pengaju masih punya dua halaman daftar. Satu daftar gabungan menuntut register pintu (opsi B) beserta sinkronisasi status, tidak sepadan untuk 1,5 komplain per bulan.
- Pemindahan lintas unit adalah dua penulisan di dua service tanpa transaksi. Idempotensi atas id komplain asal membuatnya aman diulang, bukan atomik.
- Gudang kini dapat menolak komplain tanpa dampak KPI, sehingga ada benturan kepentingan. Penyeimbangnya alasan wajib, pengaju dikabari, dan rasio `ditolak` per bulan dapat direkap (T8 di ANALISA).
- Keluhan "Lainnya" hanya hidup sebagai kabar inbox. Bila SPV tak menindaklanjuti, tak ada antrean yang mengingatkan. Bila volumenya tumbuh, itu alasan meninjau opsi B.
- Komplain atas pesanan yang tak ada di data sistem tidak dapat diajukan sama sekali.

**Yang tetap terbuka.** Daftar kategori QC menunggu tim QC. Tujuan ekspedisi dan vendor belum punya tempat (ADR 0099 K1). Kewajiban regulatif efek samping menunggu QA/RA.

**Konsekuensi deploy.**
- Kategori inbox baru (komplain dialihkan, keluhan perlu dipilah) masuk `shared-library`, jadi **notification-service naik lebih dulu**, lalu warehouse-service dan employee-service; aturan rute web ditambah di notification-service. Di MyBharata keduanya tampil "Sistem" sampai dipetakan.
- Rute internal warehouse ke employee dan sebaliknya, serta employee ke integration, kemungkinan menuntut env kunci layanan dan URL baru, jadi container terkait **dibuat ulang** (`--force-recreate`), bukan di-restart. Kepastiannya di `/plan`.
- Endpoint kategori dan field kategori QC adalah perubahan kontrak: **backend naik sebelum frontend**. Salinan kategori di frontend baru dihapus setelah endpoint ada di PROD.
- Perubahan KPI hanya di warehouse-service; bentuk respons yang dibaca employee-service tidak berubah.
- Salinan nama produk dan SKU dari `transaction_orders` ke register wajib didaftarkan di [[REF - Kepemilikan Data]] saat diimplementasikan.

**Dokumen terkait**: [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] · [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[Microservices - Warehouse Service]] · [[Microservices - Employee Service]] · [[Microservices - Integration Service]] · [[Microservices - Notification Service]] · [[APP - Web ERP]] · [[APP - MyBharata]] · [[REF - Kepemilikan Data]] · [[ADR - 0002 Database-per-Service]] · [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] · [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]]

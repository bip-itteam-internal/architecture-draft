> **Status**: ⚠️ **Sebagian diimplementasikan**, diputuskan 2026-09-17 dan disetujui pemilik proses (opsi A). **Sudah mendarat dan sudah PROD** (diukur 2026-09-21 lewat gerbang biner, bukan `docker ps` maupun `/health`): **keputusan 2** sisi register gudang (T9, bip-erp #1957 + erp-frontend #1634, merged 2026-09-17); **keputusan 7** bagian `ditolak` (T10, bip-erp #1965 + erp-frontend #1641, merged 2026-09-17), bagian `dialihkan` menunggu T13; **keputusan 3** daftar kategori tertutup QC (bip-erp #1968 + erp-frontend #1645, merged 2026-09-18); dan **keputusan 11** keamanan serta keutuhan register QC (bip-erp [#1976](https://github.com/bip-itteam-internal/bip-erp/pull/1976) merge `c2e2a1bf` + erp-frontend [#1659](https://github.com/bip-itteam-internal/erp-frontend/pull/1659) merge `b4363d97`, merged 2026-09-18). **Belum ada kodenya**: keputusan 1 dan 8 (pintu tunggal, T12), keputusan 4 (produk, SKU, dan pesanan diisi server; sisa T11), keputusan 6 ("Lainnya" ke SPV, T14). **Keputusan 5 DIREVISI 2026-09-21**: ganti kategori tinggal dalam unit sendiri, pemindahan lintas unit dibatalkan, dan T13 dicoret. Opsi C (satu register gabungan) ditimbang ULANG hari itu atas permintaan pemilik proses dan **tetap ditolak**; pengukuran dan alasannya di Context. ⚠️ Status PROD bergerak dan tak dijaga apa pun; ukur ulang sebelum dipakai memutuskan. Menggantikan **keputusan 2** [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] (pengaju memilih tujuan lebih dulu) dan memicu keputusan 12-nya. Keputusan lain ADR 0099 tetap berlaku.

## Untuk Manajemen

- **Yang berubah di layar**: semua keluhan produk diajukan lewat SATU formulir, baik dari baris ulasan marketplace maupun tanpa ulasan. Pengaju cukup memilih jenis keluhannya; unit yang akan menangani tampil sendiri dan tidak bisa diubah pengaju. Nama produk dan SKU diisi sistem dari pesanannya, jadi pengaju hanya menulis cerita keluhan dan melampirkan foto. Formulir lama "Komplain ke QC" diganti formulir ini. Bila jenis keluhannya ternyata keliru, unit penerima menolaknya dengan alasan dan pengaju mengajukan ulang lewat pintu yang sama; pemindahan otomatis antar unit tidak dibuat, sebab kejadiannya terlalu jarang untuk mesin sebesar itu. Keluhan yang tidak cocok dengan jenis mana pun diteruskan ke supervisor brand pemilik toko untuk dipilah. Komplain gudang yang ditolak tidak lagi menurunkan skor packer.
- **Siapa terdampak**: pemegang toko dan staf marketing Kyura dan Beauty Hacks (pengaju), SPV Kyura dan SPV Beauty Hacks (memilah keluhan "Lainnya"), tim gudang packing (aturan skor KPI berubah), staf QC (mendapat daftar jenis keluhan dan kini menentukan tingkat keparahan sendiri).
- **Tidak dijanjikan**:
  - Nomor batch dan tanggal kedaluwarsa **tidak** terisi otomatis. Keduanya tidak tercatat di data pesanan mana pun, jadi tetap dibaca dari foto kemasan.
  - Pesanan yang tidak ada di data sistem tidak bisa diajukan. Diukur atas ulasan buruk yang ada: 4 dari 65 untuk jalur QC, dan 20 dari 65 untuk jenis keluhan gudang karena data gudang baru ada sejak Juli 2026.
  - Tidak tersambung otomatis ke CAPA.
  - Pengaju tetap melihat nasib komplainnya di dua halaman, gudang dan QC.
  - Tetap hanya Shopee, dan keluhan untuk ekspedisi atau vendor tetap belum punya tempat.
- **Besaran kerja**: sedang, dan **berkurang satu task sejak 2026-09-21** (pemindahan lintas unit dibatalkan). Menyentuh warehouse-service, employee-service, notification-service, dan web ERP. Bagian QC menunggu tim QC menetapkan daftar jenis keluhannya; bagian gudang bisa berjalan lebih dulu.

## Deskripsi

*Satu pintu pengajuan untuk semua komplain produk. Pengaju memilih kategori, bukan unit; unit tujuan diturunkan dari register mana yang memiliki kategori itu, tanpa tabel pemetaan dan tanpa register ketiga. Produk, SKU, dan pesanan diisi server dari data pesanan. Salah unit ditangani dengan tolak lalu ajukan ulang, keluhan tanpa kategori dipilah SPV brand, dan komplain gudang yang ditolak atau dialihkan tidak lagi dihitung ke KPI packer.*

- **Path di repo**:
  - `bip-erp/services/warehouse/komplain.go` (daftar kategori diterbitkan, ganti kategori dalam unit; ~~status `dialihkan`~~ dibatalkan 2026-09-21)
  - `bip-erp/services/warehouse/kpi_komplain.go` (`ditolak` tidak dihitung; `dialihkan` tak jadi ada)
  - ~~`bip-erp/services/warehouse/komplain_alih.go`~~ **DIBATALKAN 2026-09-21** (keputusan 5)
  - `bip-erp/services/employee/quality_complaint.go` (kategori tertutup, isian server, `company_id`, race `ReplaceOne`, ganti kategori)
  - `bip-erp/services/employee/quality_complaint_akses.go` (gerbang kepemilikan toko, filter tenant, daftar putih `$set`, kunci optimistik)
  - `bip-erp/shared-library/common/toko_icc.go` (resolver kepemilikan toko, dipakai bersama warehouse-service)
  - ~~`bip-erp/services/employee/quality_complaint_alih.go`~~ **DIBATALKAN 2026-09-21** (keputusan 5)
  - `bip-erp/shared-library/models/employee/models.go` (`QualityComplaint`: kategori, identitas item, `company_id`, penanda sumber)
  - `erp-frontend/src/features/quality/complaint/lib/akses-komplain-qc.ts` (cermin gerbang baca, layar terkunci)
  - `bip-erp/shared-library/models/notification/models.go` + `bip-erp/services/notification/webpush.go` (kategori inbox baru dan aturan rute web)
  - `erp-frontend/src/features/komplain/lib/pintu.ts` (**baru** T12; fungsi murni pintu tunggal — pemetaan kategori ke unit, penurunan `title`, penyusun muatan dua kontrak. ⚠️ Komponennya TETAP di `features/integration/reviews`, lihat keputusan 8e)
  - `erp-frontend/src/features/integration/reviews/components/ajukan-komplain-modal.tsx` (jadi pintu tunggal T12) dan `erp-frontend/src/features/quality/complaint/components/complaint-form-modal.tsx` (**tidak dihapus**; mode UBAH tetap dipakai, mode BUAT jadi kode mati, lihat keputusan 8d)
  - `erp-frontend/src/features/quality/complaint/lib/rute-lama.ts` (**baru** T12, peta redirect `/icc/komplain-qc` → `/quality/komplain`) dan `erp-frontend/src/app/(main)/quality/komplain/page.tsx` (halaman gabungan dua audiens, gerbang halaman + gerbang per aksi)
  - `erp-frontend/src/features/quality/complaint/components/bukti-ulasan.tsx` (**baru** T12, bukti ulasan di dialog validasi QC — keputusan 13)
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

### Opsi C ditimbang ULANG 2026-09-21, dan tetap ditolak

Pemilik proses menanyakannya lagi dengan alasan yang sah: satu fitur hari ini dibayar di dua
service, dua kontrak, dua daur hidup, dua halaman. Ditimbang ulang dengan pengukuran baru,
bukan dengan mengulang alasan lama.

**Satu dari dua alasan penolakan TERBUKTI JAUH LEBIH LEMAH dari yang tertulis di atas.**
"KPI packer ditulis ulang" ternyata berarti menulis ulang kemampuan yang belum pernah menilai
siapa pun. Diukur PROD 2026-09-21: sumber `komplain_gudang_packing` terdaftar di kode tetapi
dipakai **nol dari 119 template KPI**; ketiga metrik yang seharusnya memakainya
(`akurasi-dan-kualitas-packing` bobot 0,10 di *Koordinator Warehouse Packing*;
`akurasi-pengiriman-produk` bobot 0,20 di *Admin Warehouse Tinggarjaya*;
`complain-rejection-maksimal-5` bobot 0,15 di *Quality Control Staff*) masih dinilai MANUAL.
Kontrol positif: 100 metrik lain di vault template memang punya blok `auto`. Ditambah tiga hal
yang melemahkannya lagi: atribusi packer **sudah didenormalisasi saat tulis** sehingga pembilang
tak lagi terikat warehouse, employee-service berbicara ke **endpoint HTTP** `/kpi/komplain-gudang`
dan bukan ke koleksinya, dan cron finalisasi malam membekukan skor sehingga pembacaan lintas
service hanya perlu hidup untuk bulan berjalan.

**Alasan kedua berdiri utuh, dan justru menguat.** Kosakata kedua register memang berbeda, dan
bentuk konkretnya baru terlihat saat diukur: gudang menyimpan kode huruf kecil
(`baru`/`diproses`/`selesai`/`ditolak`) yang dipetakan lewat i18n, sementara QC menyimpan
**kalimat Indonesia sebagai nilai status** (`"Menunggu Validasi"`) lalu merendernya mentah. Satu
koleksi gabungan memaksa salah satunya berubah, dan itu merambat ke backend. Wewenangnya juga
berbeda: gudang punya `bolehTindakLanjut` dan pengawas WMS, QC punya `bolehUbahKomplain` milik
pengaju, dan `it: staff` membuka register gudang tetapi DITOLAK di QC. Lima perbedaan cermin
akses itu masing-masing dipatok uji.

**Ongkos yang hendak dihemat ternyata kecil.** Diukur di erp-frontend: dari 1.426 baris di kedua
fitur, yang ada semata-mata karena belahan hanya **190 sampai 440 baris** (13 sampai 29 persen),
bergantung berapa banyak cakupan uji yang rela dilepas. Sisanya dua kebijakan yang memang
berbeda. Duplikasi antar-konteks yang berbeda bukan utang; penyatuan dini yang jadi utang.

**Yang benar-benar mahal bukan registernya, melainkan keputusan 5** (lihat revisinya di bawah).

⚠️ Keluhan yang mendasarinya tetap sah dan tidak dijawab ADR ini: `employee-service` memuat
Quality, Legal, R&D, Procurement, Kepatuhan, kontrak, dan mesin KPI seluruh perusahaan dalam satu
deployable (182 berkas Go non-test, 87 di antaranya `kpi_*`, diukur 2026-09-21). Bila kepemilikan
mau dirapikan, langkahnya **memberi Quality service sendiri** dengan metode
[[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] (ukur rasio kopling
dulu), BUKAN menggabungkan dua register. Menggabungkan justru menambah satu domain lagi ke
service yang sudah kelebihan muatan. Tidak diputuskan di sini dan tidak perlu diputuskan
sekarang; pemicunya harus terukur (tim berbeda, atau deploy saling menahan), bukan "terasa
berantakan".

## Decision

1. **Satu pintu untuk semua komplain produk; pengaju memilih KATEGORI, bukan unit.** Kategori ditampilkan berkelompok per unit, dan sesudah dipilih unit tujuannya tampil sebagai keterangan yang tak bisa diubah. Pintu yang sama dipakai dari baris ulasan maupun tanpa ulasan.

2. **Unit tujuan diturunkan dari register yang MEMILIKI kategori itu.** Tidak ada tabel pemetaan kategori ke unit dan tidak ada master kategori pusat: masing-masing register menerbitkan daftar kategori tertutupnya lewat endpoint baca, dan frontend menyusun pintunya dari keduanya. Satu fakta tetap tinggal di satu tempat, dan salinan tangan di frontend dihapus. ADR 0099 keputusan 1 (dua register, tanpa register ketiga) tetap berlaku.
   - *Sisi register gudang (T9, merged 2026-09-17, bip-erp #1957 + erp-frontend #1634, merged 2026-09-17, PROD 2026-09-21):* `GET /wms/komplain/kategori` membalas kode saja, berurutan, tanpa field unit (pemanggil tahu unitnya dari rute yang ia minta). Digerbang **identitas saja**, bukan gerbang baca komplain: kodenya tak rahasia, dan gerbang baca memaksa pemegang toko memanggil integration-service. Label ditulis frontend per kode (`warehouse.komplain.kategoriLabel.<kode>`); kode tanpa terjemahan tampil sebagai kodenya. Rinciannya di [[Microservices - Warehouse Service]].

3. **Register QC mendapat daftar kategori tertutup, dan isinya ditetapkan tim QC.** Usulan awal dari penggolongan ulasan: `dugaan_tidak_asli`, `segel_terbuka`, `isi_tidak_sesuai`, `kedaluwarsa`. **Tingkat keparahan ditentukan QC saat validasi**, bukan ditebak pengaju.
   - *Irisan kategori merged 2026-09-18 (bip-erp [#1968](https://github.com/bip-itteam-internal/bip-erp/pull/1968), erp-frontend [#1645](https://github.com/bip-itteam-internal/erp-frontend/pull/1645)), terverifikasi DEV lewat gateway dan layar, PROD 2026-09-21:* keempat kode di atas dipakai apa adanya, `GET /quality/complaints/kategori` digerbang identitas saja, dan kategori **wajib** di POST maupun PUT. Alasan "wajib di PUT" berubah pada 2026-09-18: dulu karena `ReplaceOne` mengganti dokumen utuh, sekarang karena kategori memang field yang divalidasi di daftar putih `$set` (keputusan 11). Rinciannya di [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] dan [[API - Employee Service]].
   - ⚠️ **Empat penyimpangan sadar dari keputusan ini dan keputusan lain di bawah**, dicatat supaya tak terbaca sebagai kelalaian:
     1. Daftar disetujui **pemilik proses atas nama tim QC**, bukan ditetapkan tim QC. Itu menutup K4 sementara; QC masih boleh meminta perubahan. ⚠️ **Batasnya bukan lagi "sebelum naik ke PROD"**, sebab kategori sudah PROD 2026-09-21. Yang membuatnya masih murah adalah registernya masih kosong (diukur PROD 2026-09-21: koleksi `quality_complaint` sudah tercipta, **0 dokumen**, kontrol positif `work_data` 215). Jendela ini akan tertutup oleh komplain pertama yang masuk, bukan oleh deploy.
     2. ~~**`company_id` dan race `ReplaceOne` DITUNDA**~~ **DITUTUP 2026-09-18** oleh irisan keamanan dan keutuhan (keputusan 11 di bawah). Penundaannya berlangsung satu hari; keputusan 10 dan keputusan 12 [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] kini terpenuhi.
     3. **Formulir `/icc/komplain-qc` tetap diubah** walau keputusan 8 merencanakan penggantiannya oleh pintu tunggal (T12). Label, hook, dan pembaca keadaan kategorinya dipakai ulang T12, jadi yang terbuang hanya penempatan isiannya. *Terbukti benar: T12 memakai ulang ketiganya, dan komponennya sendiri tetap hidup untuk mode UBAH (lihat keputusan 8).*
     4. ~~**`severity` masih diisi pengaju**, belum pindah ke QC seperti kalimat di atas. Menunggu sisa T11.~~ **DITUTUP 2026-09-21 oleh T12.** Tingkat keparahan kini ditentukan QC di dialog validasi, dan backend menutup jalur pengaju dari DUA sisi sekaligus: `severity` dicabut dari daftar putih sunting **dan** dikosongkan paksa saat POST. Mencabutnya dari PUT saja tidak cukup, sebab pengaju masih bisa menentukannya sekali di saat mengajukan sehingga gerbang di rute sunting jadi penjaga pintu yang jendelanya terbuka.
        - **Nilainya ikut dikodekan** (`ringan`/`sedang`/`berat`, sebelumnya kalimat berkapital). Ini melebihi yang semula disetujui, disebut lebih dulu, dan disetujui: alasannya persis sama dengan status di keputusan 8a di bawah, dan memindahkan kepemilikan field tanpa sekalian mengkodekannya berarti menanam ulang cacat yang baru saja dicabut, di dokumen yang sama.
        - **Rute `validate` satu-satunya penulisnya**, dan ia difilter `menunggu_validasi`. Konsekuensi yang diterima sadar: **sesudah divalidasi, tingkat keparahan tak bisa dikoreksi lewat endpoint mana pun**; satu-satunya jalan keluar menghapus komplainnya. Belum ada yang menuntut koreksi, jadi tidak dibangun.
        - Nilai kosong berarti "tidak diubah", bukan "kosongkan", supaya klien lama tetap bisa memvalidasi tanpa diam-diam menghapus tingkat yang sudah diisi QC lain.

4. **Produk, SKU, dan pesanan diisi SERVER.** Pengaju hanya mengirim nomor pesanan dan identitas item, yang dari baris ulasan sudah terbawa. Register mengambil nama produk dan SKU dari data pesanan integration-service lalu menyalinnya; nilai serupa dari klien diabaikan. Pesanan yang tak ditemukan ditolak dengan pesan yang menjelaskan sebabnya. Tanpa ulasan, pengaju memasukkan nomor pesanan, server mengeceknya, lalu pengaju memilih produk dari isi pesanan itu. Salinan ini bertanggal dan tak berubah bila datanya kelak disunting, prinsip yang sama dengan ADR 0099 keputusan 4.
   - Register gudang tetap per **pesanan**, tidak per item, dan tetap memverifikasi ke `fulfillment_orders` seperti sekarang. Register QC per **item**.
   - ⛔ Data pesanan diambil **server ke server**, tidak lewat layar pengaju, karena memuat data pembeli yang tidak dibutuhkan untuk mengajukan komplain. Endpoint pilih-produk untuk pengaju hanya mengembalikan item.
   - Gerbang tulis register QC mengikuti register gudang: pemegang toko atas tokonya sendiri, atau staf marketing. Ini meneruskan koreksi ADR 0099 bahwa hak mengajukan diturunkan dari kepemilikan toko.

5. **Unit penerima dapat mengganti kategori DALAM UNITNYA SENDIRI.** Kategorinya cukup diubah, dan register gudang menjaga indeks unik `(order_id, kategori)` sehingga bentrok wajib berbunyi 409 bersebab.

   ⛔ **Pemindahan LINTAS unit DIBATALKAN 2026-09-21.** Rancangan aslinya (dipertahankan di bawah sebagai catatan, jangan dikerjakan) berbunyi: service asal membuat komplain di register tujuan lewat rute internal berkunci layanan, idempoten atas id komplain asal; baru sesudah itu komplain asal ditandai `dialihkan`, status akhir yang merujuk komplain tujuan; alasan wajib; pengaju dan unit tujuan dikabari; tanpa persetujuan pengaju.

   **Kenapa dibatalkan.** Ia mesin yang mahal untuk kejadian yang jarang. Volumenya **1,5 komplain per bulan** yang dapat ditindak unit yang ada (terukur, lihat Context), dan salah unit adalah bagian kecil dari itu. Yang harus dibangun: rute internal di KEDUA service, idempotensi atas id lintas register, status akhir baru, dua kategori inbox baru berikut urutan deploy notification-service, plus **dua penulisan di dua service tanpa transaksi** yang sudah diakui sendiri di Consequences. Alasan yang sama persis dipakai ADR ini untuk menolak opsi B: "berat untuk 1,5 per bulan". Alasan itu berlaku untuk keputusan ini juga, dan tidak diterapkan pada dirinya sendiri saat ditulis.

   **Yang dipakai sebagai gantinya**: unit penerima **menolak** dengan alasan, pengaju mengajukan ulang lewat pintu yang sama dengan kategori yang benar. Jalur tolak sudah ada, sudah PROD, dan penolakan tanpa alasan sudah dibalas 400 oleh backend (keputusan 7). Ongkosnya satu tindakan manusia beberapa kali setahun.

   ⚠️ **Yang dipertukarkan, diterima sadar**: komplain yang salah alamat kehilangan jejaknya sebagai satu perkara, sebab yang diajukan ulang adalah dokumen baru. Bila kelak volumenya naik atau rekap lintas unit menuntut jejak itu, keputusan ini ditinjau ulang; rancangannya sudah tertulis di atas dan tinggal dikerjakan. **Status `dialihkan` karena itu TIDAK dibuat**, dan keputusan 7 di bawah yang menyebutnya menjadi bersyarat pada peninjauan itu.

6. **Keluhan "Lainnya" tidak disimpan di register mana pun.** Formulir mengirim kabar inbox kepada SPV brand pemilik toko, ditemukan lewat resolver atasan yang sudah ada, berisi tautan ke ulasan atau pesanannya. SPV mengajukan ulang lewat pintu yang sama dengan kategori yang benar. Bila tak ada SPV yang ditemukan, pengaju diberi tahu di layar, bukan dibiarkan senyap.

7. **KPI gudang packing: `ditolak` TIDAK dihitung ke `KomplainPacking`.** `ditolak` wajib disertai alasan tindak lanjut; pengaju sudah dikabari saat komplain ditutup (ADR 0099 keputusan 8). Ini perubahan aturan angka penilaian orang, jadi tim gudang diberi tahu sebelum naik ke PROD. ⚠️ **Bagian `dialihkan` gugur 2026-09-21** bersama keputusan 5: statusnya tak jadi dibuat, jadi tak ada yang perlu dikecualikan. ⛔ **Utang yang belum dibayar dan jatuh tempo**: aturan ini sudah PROD sejak 2026-09-21, dan kalimat "tim gudang diberi tahu sebelum naik ke PROD" di atas belum terbukti dijalankan.
   - *Bagian `ditolak` (T10, merged 2026-09-17, bip-erp #1965, PROD 2026-09-21):* yang ditolak dikeluarkan dari pembilang, dari cacah per kategori, dan dari cacah per packer. Penolakan tanpa alasan dibalas 400 oleh backend, bukan hanya dicegah layar, karena begitu yang ditolak tak dihitung, penolakan tanpa alasan menjadi jalan menghapus komplain dari penilaian tanpa jejak. Cacah yang ditolak diterbitkan terpisah sebagai `komplain_ditolak` dan ditulis di catatan penilaian, supaya gudang yang menolak semua komplain tetap terlihat; field itu **bukan** komponen akurasi dan tidak boleh dijumlahkan ke `komplain_packing` (kontraknya di [[API - Warehouse Service]]). Skor periode yang sudah tersimpan tidak dihitung ulang.

8. **Formulir `/icc/komplain-qc` diganti pintu tunggal.** Halaman daftar tetap per unit: `/warehouse/komplain` dan `/quality/komplain`.

   ✅ **Dikerjakan T12 2026-09-21** (kode selesai dan terverifikasi lokal; **belum push, belum PR, belum merge, belum DEV, belum PROD** — jangan dibaca sebagai sudah mendarat). Lima penyimpangan sadar, dicatat supaya tak terbaca sebagai kelalaian:

   a. ⛔ **Rute lama diberi REDIRECT permanen, bukan dibiarkan 404**, walau keputusan ini menulis "diganti". Alasannya bukan kesopanan: redirect ke halaman yang tak ada **gagal SENYAP** di Next.js App Router (200, bukan 404) karena rute dinamis menangkap segmen apa pun, jadi tujuannya dikunci peta teruji `features/quality/complaint/lib/rute-lama.ts` yang memeriksa ke berkas di disk berikut kontrol negatif, bukan URL yang diketik di `page.tsx`.

   b. **`/quality/komplain` jadi halaman GABUNGAN dua audiens**, bukan sekadar halaman QC yang tetap. Keputusan ini tidak menyebut ke mana marketing memantau nasib komplainnya sesudah halamannya hilang, dan jawabannya: entri menu KEDUA berjudul "Komplain ke QC" di Marketing › Pekerjaan Saya menunjuk ke halaman yang sama, pola yang sudah dipakai `/warehouse/komplain`. Konsekuensinya halaman itu WAJIB menggerbangi dirinya sendiri dan tiap aksinya, dan itulah yang menutup butir pertama T15.

   c. ⛔ **Rute itu SENGAJA tidak dimasukkan ke `qualityPrivateRoutes` milik proxy.** Daftar itu mengalihkan siapa pun TANPA peran `quality` ke `/dashboard`, jadi menambahkannya justru akan mengunci marketing dari halaman yang baru saja dijadikan rumahnya — kebalikan dari yang dikerjakan T12. Preseden yang diikuti `/warehouse/komplain`, yang juga dibaca dua audiens dan juga nol kemunculan di `proxy.ts`. Halaman bersama digerbang cerminnya sendiri plus backend, bukan oleh daftar rute per departemen.

   d. **`ComplaintFormModal` TIDAK dihapus** walau keputusan ini menyebutnya diganti, sebab mode UBAH-nya satu-satunya cara mengoreksi komplain yang sudah diajukan dan pintu tunggal tak punya mode itu. ⚠️ Konsekuensinya mode BUAT komponen itu kini **kode mati**: satu-satunya pemanggilnya berkas ujinya sendiri. Dibiarkan menunggu keputusan 4 (pintu tanpa ulasan), bukan dicabut sekarang.

   e. **Komponen pintunya tetap di `features/integration/reviews`**, hanya fungsi murninya yang pindah ke `features/komplain/lib/pintu.ts`. Path di repo di atas menulis `features/komplain/` sebagai rumah formulirnya; yang benar-benar tinggal di sana cuma logika yang bisa diuji tanpa merender Radix.

   ⚠️ **Yang TIDAK ikut mendarat**: pintu **tanpa ulasan** (nomor pesanan dicek server lalu pilih produk) tetap ditunda menunggu endpoint pilih-produk di keputusan 4, jadi T12 melayani pengajuan dari baris ulasan saja. Akibat yang perlu diketahui: sejak tombol buat hilang dari halaman daftar, **tak ada jalan mengajukan komplain QC yang tidak bersumber dari baris ulasan marketplace**, dan tak satu pun layar memberi tahu ke mana harus pergi.

9. **Tidak disambungkan ke CAPA sekarang.** CAPA belum pernah terisi di PROD, jadi sambungan otomatis akan dibangun di atas modul yang belum dipakai. QC membuat CAPA sendiri bila perlu. Ditinjau ulang begitu CAPA benar-benar dipakai.

10. **ADR 0099 keputusan 5, 6, 7, 9, 10, dan 11 tetap berlaku**: kategori dipilih manusia, tujuan tanpa register tidak dipaksakan, "tidak mempan" tidak menjadi komplain, tanpa SLA, hanya Shopee, dan kategori efek samping ditahan. **Keputusan 12 terpicu**: `company_id` dan race `ReplaceOne` register QC dikerjakan bersama perubahan register itu. *Terpenuhi 2026-09-18, keputusan 11 di bawah.*

11. **Keamanan dan keutuhan register QC** (diputuskan 2026-09-18; **merged 2026-09-18** lewat bip-erp [#1976](https://github.com/bip-itteam-internal/bip-erp/pull/1976) merge `c2e2a1bf` dan erp-frontend [#1659](https://github.com/bip-itteam-internal/erp-frontend/pull/1659) merge `b4363d97`, backend lebih dulu; ✅ **PROD 2026-09-21**, diukur lewat gerbang biner. Rencana penahanan merge sampai blok deploy PROD gabungan T3 dan T9 mendarat tidak jadi dipakai).

    a. **Cakupan BACA komplain QC = seluruh komplain di perusahaan pembaca**, bukan hanya komplain yang ia ajukan sendiri. ⚠️ Ini keputusan BARU, bukan penerapan keputusan lama: sampai hari ini vault mencatat visibilitas register QC sebagai belum pernah diputuskan siapa pun. Alasannya, tabel `/icc/komplain-qc` memang dirancang menampilkan komplain satu tim supaya pengaju tahu masalah yang sama sudah dilaporkan orang lain, dan menyempitkannya ke pengaju sendiri membuat kolom "siapa pengajunya" tak pernah punya alasan untuk ada.

    b. **Kepemilikan toko di register QC dipakai sebagai IZIN MASUK, BUKAN cakupan baris.** ⛔ Ini berbeda dari register gudang, dan bedanya wajib diketahui siapa pun yang memasang paket izin: di gudang `cakupanTokoKomplain` menyempitkan `shop_id` sehingga pemegang tanpa toko melihat nol baris, sementara `QualityComplaint` tak punya `shop_id` sama sekali dan `order_ref`-nya masih teks bebas. Satu-satunya penyempit barisnya `company_id`. Konsekuensinya siapa pun yang lolos gerbang baca melihat seluruh komplain QC perusahaannya, termasuk milik brand lain, dan termasuk bila ia tak memegang satu toko pun. Diterima sadar, dan **wajib ditinjau ulang** begitu keputusan 4 mendarat dan komplain QC punya identitas item yang berasal dari pesanan.

    c. **Izin `akuntoko.komplain.work` membuka BACA komplain QC, tetapi tidak membuka pengajuan.** Mengajukan tetap diturunkan dari kepemilikan toko. Asimetri ini disengaja: yang berhak menuding kesalahan QC adalah orang yang benar-benar memegang tokonya, bukan siapa pun yang kebetulan dipasangi paketnya. Ini memenuhi keputusan 5 [[ADR - 0107 Alat Kerja Pemegang Akun Toko lewat Izin Posisi akuntoko]], yang menahan menu Komplain ke QC sampai gerbang ini mendarat.

    d. **Tulis memakai `CompanyID`, baca memakai `EffectiveCompanyID`** ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]). Daftar adalah satu-satunya jalur yang menghormati `?company=` milik admin pusat; seluruh jalur tulis terkunci ke perusahaan pemanggil tanpa override, kalau tidak `?company=` berubah jadi alat menyunting data tenant lain.

    e. **Penyuntingan memakai daftar putih, bukan penggantian dokumen utuh.** `ReplaceOne` diganti `$set` berisi hanya field yang memang boleh disunting, sehingga `company_id`, `status`, `verdict`, `reason`, `validated_by`, `validated_at`, dan `metadata.created_*` tak bisa disentuh rute sunting sama sekali. Penjaga yang berbentuk ketiadaan tak bisa lupa dijalankan. Daftar lengkapnya, beserta kewajiban memutuskan keanggotaan tiap field baru, ada di [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]].

    f. **Tiga bentrok tulis dijawab 409, bukan ditimpa diam-diam**: validasi QC yang mendarat saat pengaju sedang menyunting, dua penyunting serentak (kunci optimistik `metadata.updated_at`, sebab status saja tidak memisahkan mereka), dan dua staf QC yang memvonis komplain yang sama.

12. **Kosakata status, verdict, dan tingkat keparahan register QC jadi KODE, bukan kalimat** (diputuskan 2026-09-21 saat `/plan` T12, opsi B dari dua yang disajikan; kode selesai, **belum merge**).

    Nilai tersimpan berubah dari `"Menunggu Validasi"` · `"Valid"` · `"Ditolak"` jadi `menunggu_validasi` · `valid` · `ditolak`, dan tingkat keparahan dari `"Ringan"`/`"Sedang"`/`"Berat"` jadi `ringan`/`sedang`/`berat`.

    **Kenapa nilainya, bukan tampilannya saja.** Kolom Status kedua layar QC tak pernah bisa ikut bahasa aktif, sebab yang dirender adalah kalimat Indonesia yang tersimpan di dokumen ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]). Register komplain gudang tetangga menyimpan kode huruf kecil lalu memetakannya lewat i18n sejak awal. Membetulkan tampilannya saja berarti memasang peta kalimat-ke-label yang harus dijaga sama dengan disiplin, di dua register yang sudah berbeda kosakata. **Waktunya yang menentukan**: registernya masih **nol dokumen** di PROD (diukur 2026-09-21), jadi perubahan ini tak pernah semurah ini lagi. Begitu komplain pertama masuk, yang sama menjadi migrasi data.

    ⛔ **Ongkosnya: tidak ada urutan deploy yang aman.** Ini pecah-kontrak, bukan penambahan field, jadi konvensi tim "BE sebelum FE, FE fallback aman bila field baru belum ada" **tidak berlaku**. Kedua sisi memeriksa `verdict` KETAT, sehingga jendela rusaknya dua arah: klien lama mengirim `"Valid"` ke backend baru dibalas **400** `verdict harus valid atau ditolak`, dan klien baru mengirim `"valid"` ke backend lama dibalas **400** `verdict harus 'Valid' atau 'Ditolak'`. Kerusakan turunannya senyap: `bolehUbahKomplain` membandingkan status sehingga tombol Ubah hilang untuk semua baris, dan label status jatuh ke kode mentah yang terbaca "memang begitu tampilannya".

    **Yang diputuskan sebagai gantinya** (2026-09-21): tidak ada jendela transisi di backend dan tidak ada migrasi data. Sebelum deploy, **jumlah dokumen `quality_complaint` di PROD diukur ulang tepat saat itu**, bukan dikutip dari catatan; bila masih nol, employee-service dan frontend dinaikkan berdekatan dan jendela rusaknya diterima. ⚠️ Bila ternyata sudah ada dokumen, dokumen berkalimat lama tak cocok filter `menunggu_validasi` sehingga barisnya mustahil disunting (PUT) maupun divonis (validate, 409) dan tombolnya ikut hilang di layar; saat itu keputusan ini menuntut skrip migrasi lebih dulu.

    ⚠️ **Penjaganya hanya dari satu ujung.** Frontend mengunci ketiga nilai sebagai literal di test; sisi Go mengunci status tetapi belum mengunci daftar `severity`. Kontrak lintas-repo yang dijaga satu ujung akan menyimpang diam-diam.

13. **Salinan ulasan di register QC adalah klaim KLIEN, bukan data berprovenans server** (T12, 2026-09-21). Kelima field (`bukti_foto`, `ulasan_comment_id`, `ulasan_channel`, `ulasan_teks`, `ulasan_bintang`) dinamai **persis** seperti register gudang supaya kedua register bisa dibaca dengan kebiasaan yang sama, dan itu memenuhi [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] keputusan 4 untuk jalur QC.

    ⛔ **Tapi aturan isinya TIDAK sama, dan justru kesamaan nama itu yang menyesatkan.** Register gudang membersihkan di server: `bintangUlasanWaras` memaksa nilai di luar 1..5 jadi 0, ketiga string di-`TrimSpace`, dan `sumber` diturunkan dari isinya. Jalur QC mem-`BodyParser` langsung ke model, jadi `ulasan_bintang: 99` tersimpan apa adanya dan tak ada yang memverifikasi bahwa ulasannya ada atau bahwa ia milik toko pengaju. Satu nama, dua domain nilai yang sah — **jangan merata-ratakan kedua register jadi satu angka**. Untuk sekarang rentangnya dijepit di LAYAR (bintang di luar 1..5 tidak digambar), dan menambal di sumbernya masih utang.

    Yang sudah aman: kelimanya **tak pernah masuk daftar putih sunting**, jadi bukti tak bisa berubah sesudah QC mulai memeriksa. Dan sejak T12 buktinya benar-benar **dirender** di dialog validasi; sebelum itu kelima field disimpan tanpa pernah tampil di satu titik pun, sehingga QC memvonis tanpa melihat dasar tudingannya dan pemeriksaan basis data tetap berkata semuanya benar.

## Consequences

**Yang membaik.** Pengaju tak perlu tahu struktur organisasi, dan keluhan yang salah jenis tidak lagi menghukum packer. Nama produk dan SKU di komplain QC dapat dipercaya karena berasal dari pesanan. Salinan tangan kategori di frontend hilang, sehingga menambah kategori di backend langsung terlihat di pintu.

**Yang memburuk, dan diterima sadar.**
- Pengaju masih punya dua halaman daftar. Satu daftar gabungan menuntut register pintu (opsi B) beserta sinkronisasi status, tidak sepadan untuk 1,5 komplain per bulan.
- ~~Pemindahan lintas unit adalah dua penulisan di dua service tanpa transaksi.~~ **Tidak jadi dibayar**: keputusan 5 direvisi 2026-09-21, salah unit ditangani dengan tolak lalu ajukan ulang. Konsekuensinya berpindah: komplain salah alamat kehilangan jejaknya sebagai satu perkara.
- Gudang kini dapat menolak komplain tanpa dampak KPI, sehingga ada benturan kepentingan. Penyeimbangnya alasan wajib, pengaju dikabari, dan rasio `ditolak` per bulan dapat direkap (T8 di ANALISA).
- Keluhan "Lainnya" hanya hidup sebagai kabar inbox. Bila SPV tak menindaklanjuti, tak ada antrean yang mengingatkan. Bila volumenya tumbuh, itu alasan meninjau opsi B.
- Komplain atas pesanan yang tak ada di data sistem tidak dapat diajukan sama sekali.
- Keputusan 11b: pemegang paket "Marketing: Pemegang Akun Toko" yang belum memegang satu toko pun tetap membaca seluruh komplain QC perusahaannya. Di register gudang orang yang sama melihat nol baris. Dua menu yang digerbang izin yang sama karena itu berbeda cakupan, dan itu ditulis terang di [[CORE - RBAC dan Permission Set]] supaya yang memasang paketnya tahu.
- Keputusan 11a: pemegang toko membaca komplain brand lain di perusahaannya. Yang dipertukarkan adalah kerahasiaan antar-brand demi tabel yang berguna bagi satu tim; bila brand kelak menuntut pemisahan, penyempitnya sudah tersedia begitu keputusan 4 mendarat.

- Keputusan 12: mengubah kosakata nilai membeli layar yang bisa berbahasa dengan harga **jendela deploy yang rusak dua arah** pada rute validate. Dibayar sekarang justru karena registernya masih kosong; menundanya berarti membayar migrasi data untuk keuntungan yang sama.
- Keputusan 8d: mode BUAT `ComplaintFormModal` jadi kode mati, dan **tak ada jalan mengajukan komplain QC di luar baris ulasan marketplace** sampai keputusan 4 mendarat. Tak satu pun layar memberi tahu itu, jadi orang yang membuka menu "Komplain ke QC" melihat tabel tanpa cara mengisinya.
- Keputusan 3 (severity): salah pilih tingkat keparahan **permanen**, sebab satu-satunya penulisnya rute validate yang hanya jalan sekali. Belum ada yang menuntut koreksi, jadi tidak dibangun; bila kelak dituntut, itu menuntut rute baru, bukan pelonggaran filter.

**Yang tetap terbuka.** Daftar kategori QC menunggu tim QC. Tujuan ekspedisi dan vendor belum punya tempat (ADR 0099 K1). Kewajiban regulatif efek samping menunggu QA/RA. Komplain QC yang dibuat lewat token layanan tanpa `BIP-Employee-ID` masih berujung `created_by` kosong, dan tabel `/icc/komplain-qc` masih belum menampilkan nama pengajunya; keduanya tak disentuh keputusan 11.

**Konsekuensi deploy.**
- Kategori inbox baru tinggal SATU (keluhan perlu dipilah, keputusan 6); yang untuk komplain dialihkan gugur bersama keputusan 5 pada 2026-09-21. Ia masuk `shared-library`, jadi **notification-service naik lebih dulu**, lalu service pengirimnya; aturan rute web ditambah di notification-service. Di MyBharata ia tampil "Sistem" sampai dipetakan.
- Rute internal warehouse ke employee dan sebaliknya, serta employee ke integration, kemungkinan menuntut env kunci layanan dan URL baru, jadi container terkait **dibuat ulang** (`--force-recreate`), bukan di-restart. Kepastiannya di `/plan`.
- Endpoint kategori dan field kategori QC adalah perubahan kontrak: **backend naik sebelum frontend**. Salinan kategori di frontend baru dihapus setelah endpoint ada di PROD.
- Perubahan KPI hanya di warehouse-service; bentuk respons yang dibaca employee-service tidak berubah.
- Salinan nama produk dan SKU dari `transaction_orders` ke register wajib didaftarkan di [[REF - Kepemilikan Data]] saat diimplementasikan.
- Keputusan 11 menyentuh `shared-library/common` dan `shared-library/models/employee`, jadi **employee-service dan warehouse-service naik bersama**: resolver kepemilikan toko kini dipakai keduanya lewat `common.TokoICCMilik`. Tanpa env baru (diperiksa di container PROD 2026-09-18: `INTEGRATION_MODULE_URL` dan `INTERNAL_GATEWAY_KEY` sudah terisi di Employee-Service), tanpa kategori inbox baru, dan tanpa migrasi data (koleksi `quality_complaint` belum tercipta di PROD, nol dokumen di DEV, diukur 2026-09-18). Indeks `{company_id, status}` dibuat sendiri saat boot dan idempoten.
- Keputusan 11c mengubah izin yang menggerbangi menu Komplain ke QC, jadi **backend naik sebelum frontend**. Frontend yang naik duluan memunculkan menu bagi pemegang paket dan tiap aksinya berakhir 403, persis keadaan yang dihindari [[ADR - 0107 Alat Kerja Pemegang Akun Toko lewat Izin Posisi akuntoko]].

**Dokumen terkait**: [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] · [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[Microservices - Warehouse Service]] · [[Microservices - Employee Service]] · [[Microservices - Integration Service]] · [[Microservices - Notification Service]] · [[APP - Web ERP]] · [[APP - MyBharata]] · [[REF - Kepemilikan Data]] · [[ADR - 0002 Database-per-Service]] · [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] · [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]]

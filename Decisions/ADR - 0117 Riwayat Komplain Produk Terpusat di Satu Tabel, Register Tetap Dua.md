> **Status**: 🟡 **Diusulkan**, kodenya belum ada. Pekerjaan pertamanya (memasang paket izin `marketing_akuntoko_pemegang` ke pemegang toko) adalah master data dan **tidak menunggu ADR ini**. Diukur prod 2026-09-22: kedua register komplain nol dokumen dan paket izin itu dipasang ke nol orang, sehingga 36 pemegang toko belum melihat satu pun menu komplain. Daftar task: [[ANALISA - Riwayat Komplain Produk Terpusat]].

## Untuk Manajemen

Pemegang akun toko, leader, dan SPV mendapat **satu halaman berisi seluruh riwayat komplain produk**, keluhan pekerjaan gudang dan keluhan mutu dalam satu tabel dengan kolom yang sama, urut dari yang paling lama menggantung, dan bisa dicari per nomor pesanan. Sekarang riwayat itu terpecah di dua halaman milik dua departemen lain, sehingga orang yang mengajukan harus membuka dua tempat untuk tahu nasib laporannya. Tim gudang dan staf QC tetap bekerja di halamannya masing-masing; yang digabung hanya bacaannya.

**Terdampak**: 36 Account Specialist yang memegang toko, SPV Kyura dan Beauty Hacks, tim gudang packing, dan staf QC. Cara mengajukan komplain tidak berubah sama sekali.

**Yang TIDAK dijanjikan**:

1. **Halaman ini bukan yang membuat komplain mulai masuk.** Diukur di produksi 22 September 2026, kedua register **nol dokumen**, dan sebabnya bukan jumlah tabel: ke-36 pemegang toko tidak melihat satu pun menu komplain karena paket izinnya belum dipasang ke siapa pun. Itu dikerjakan lebih dulu sebagai pekerjaan pertama, dan tanpa itu halaman ini akan kosong bagi audiens utamanya.
2. **Bukan rekap berangka.** Ia daftar baris untuk menagih dan mencari, bukan laporan per periode. Rekap kategori yang berulang dan bahan laporan ke manajemen diputuskan setelah ada data nyata.
3. **Tidak mengubah siapa yang berwenang memutuskan apa pun.** Gudang tetap yang menutup komplain gudang, QC tetap yang memvonis komplain mutu.
4. **Tetap hanya Shopee**, dan keluhan yang tujuannya ekspedisi atau vendor tetap belum punya tempat.
5. **Sampai identitas item komplain mutu berasal dari data pesanan**, baris komplain mutu belum bisa disempitkan per toko. Selama itu, tabel menandai tiap baris apakah ia milik pembaca, dan pembaca tetap melihat baris brand lain.

**Besaran kerja**: sedang. Satu endpoint agregat baru di employee-service yang memungut dua register, satu halaman web baru, dan satu pekerjaan master data yang bisa jalan hari ini tanpa deploy apa pun.

## Deskripsi

*Riwayat komplain produk dibaca dari satu tabel seragam yang dirakit agregator di employee-service dari kedua register yang sudah ada, dengan kosakata status dipetakan di agregator dan bukan di layar, sementara register, gerbang, wewenang, dan sambungan KPI tetap milik unit masing-masing.*

- **Path di repo**:
  - `bip-erp/services/employee/komplain_riwayat.go` **(baru)** — agregator, bersaudara dengan `ringkasan_pengajuan.go`
  - `bip-erp/services/employee/ringkasan_pengajuan.go` — pola yang dipakai ulang (registri sumber, batas waktu per sumber, balasan `{data, degraded}`)
  - `bip-erp/services/warehouse/komplain.go` — endpoint daftar yang dipungut, tidak diubah
  - `bip-erp/services/employee/quality_complaint.go` — endpoint daftar yang dipungut, tidak diubah
  - `erp-frontend/src/app/(main)/marketing/komplain/page.tsx` **(baru)**
  - `erp-frontend/src/features/komplain/lib/baris.ts` **(baru)** — pembaca bentuk seragam; `features/komplain/lib/pintu.ts` sudah ada dan tidak disentuh
  - `erp-frontend/src/components/layout/sidebar-menus.tsx`
  - Master data `master_permission_set` key `marketing_akuntoko_pemegang` — dipasang ke pemegang toko, bukan berkas repo
- **Tanggal**: 2026-09-22
- **Terkait**: [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] · [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] · [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] · [[ADR - 0107 Alat Kerja Pemegang Akun Toko lewat Izin Posisi akuntoko]]

## Context

Kebutuhan datang sebagai solusi: "riwayat komplain produk harusnya terpusat jadi satu tabel, supaya memudahkan pemegang toko, leader, dan SPV". Ditanyakan balik apa yang diputuskan dari tabel itu, pemilik proses menyatakan **keempat** kegunaannya berlaku: menagih komplain yang menggantung, menilai masalah yang berulang, mencari cepat per nomor pesanan, dan menyiapkan bahan laporan ke atasan.

### Yang terukur di PROD 22 September 2026

Seluruhnya baca saja, dengan kontrol positif supaya nol dapat dibedakan dari akses yang gagal.

| Yang diukur | Hasil | Kontrol positif |
|---|---|---|
| `warehouse_komplain_gudang` | **0 dokumen** | 142.414 `fulfillment_orders` di DB yang sama |
| `quality_complaint` | **0 dokumen** | 215 `work_data` di DB yang sama |
| Paket `marketing_akuntoko_pemegang` ("Marketing: Pemegang Akun Toko") | Ada di katalog, dua izin utuh, **dipasang ke nol orang** | 36 koleksi `employee_db` dipindai seluruhnya, nol menyebut `akuntoko` |
| Account Specialist | 36 orang, seluruhnya berakun aktif | 0 tanpa dokumen autentikasi |
| Peran mereka | `insentive:icc` 29, `insentive:crm` 1, `insentive:affiliate` 1 | |
| Peran `kyura` atau `beauty_hacks` di antara mereka | **0 dari 36** | |
| Notifikasi saat ulasan bintang rendah masuk | nol pemanggilan di jalur ulasan integration-service | pola pencarian yang sama menemukan 13 dan 22 kecocokan di dua berkas notifikasi lain |

### Kenapa registernya nol, dan ini bukan soal jumlah tabel

Ketiga menu komplain marketing digerbang izin `akuntoko.komplain.work`, dengan fallback `bolehKomplain`. Fungsi itu meloloskan `kyura`/`beauty_hacks` dari tingkat staf, `it` dari tingkat supervisor, dan modul `insentive` **hanya** pada tier `adv_leader`/`adv_meta`/`adv_marketplace` (`erp-frontend/src/features/marketing-analytics/constants/izin.ts:155-252`). Pemegang toko sungguhan berperan `insentive:icc`, yang tidak termasuk, dan paketnya tidak dipasang ke siapa pun. Jadi ke-36 orang itu tidak melihat menu Ulasan, Komplain ke Gudang, maupun Komplain ke QC.

Backend justru sudah dibetulkan untuk mereka: hak baca dan hak mengajukan kedua register sudah diturunkan dari `icc_account_mappings`, bukan dari daftar peran. Pintunya ada, pegangannya belum dipasang. Ini kelas cacat yang sudah bernama di [[REF - Alur Persetujuan]]: **wewenang tanpa kemampuan melihat**, yang gejalanya bukan penolakan melainkan "tak ada apa-apa".

### Yang sudah ada, dan sudah jauh

[[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] sudah memutuskan pola tabel seragam beserta mesinnya, dan irisan pertamanya **sudah mendarat** di `origin/main` (`erp-frontend/src/app/(main)/portal/persetujuan/page.tsx`, `src/features/persetujuan/`). Yang dipakai ulang dari sana: agregator tinggal di employee-service karena ia sudah memegang registri lintas modul dan bukan pemilik antrean mana pun; kolom perihal diisi satu kalimat jadi oleh agregator sehingga layar tak perlu tahu bentuk data tiap modul; pemetaan kosakata dikerjakan di agregator; baris yang tak bisa ditindak pembaca tetap tampil bertanda; dan tiap kategori wajib menyatakan di mana detailnya dibuka sebelum barisnya boleh masuk tabel.

⚠️ Agregator **barisnya** belum ada: di `origin/main` employee-service baru punya `ringkasan_pengajuan.go` (agregator angka), sedangkan `antrean_persetujuan.go` milik irisan 2 ADR 0114 belum dikerjakan. Jadi ADR ini memakai ulang **mekanisme** `ringkasan_pengajuan.go`, bukan endpoint yang sudah jadi.

### Dua kosakata status untuk hal yang sama

Register gudang menyimpan kode huruf kecil `baru`/`diproses`/`selesai`/`ditolak`; register QC menyimpan `menunggu_validasi`/`valid`/`ditolak` sejak kosakatanya dikodekan. Layar yang memetakan keduanya sendiri akan menyimpang begitu satu register menambah nilai baru, dan gejalanya baris yang jatuh ke kategori salah tanpa satu pun galat. Ini alasan yang sama yang membuat ADR 0114 menaruh pemetaan di agregator, di sana untuk enam kosakata, di sini untuk dua.

### Cakupan baris kedua register TIDAK sebanding

Di register gudang, `cakupanTokoKomplain` menyempitkan `shop_id`, sehingga pemegang toko melihat komplain tokonya dan orang yang belum dipetakan melihat nol baris. Di register QC kepemilikan toko hanya izin masuk: `QualityComplaint` tidak punya `shop_id` sama sekali dan `order_ref`-nya masih teks bebas, jadi satu-satunya penyempit barisnya `company_id` dan siapa pun yang lolos membaca seluruh komplain QC perusahaannya. Menggabungkan keduanya apa adanya menyandingkan baris milik tokonya dengan baris milik semua orang, tanpa cara membedakannya. Itu yang menuntut penanda per baris di keputusan 6.

### Alasan penolakan di ADR 0103 keliru, dan itu dikoreksi di sini

[[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] menutup pintu ini dengan satu kalimat di Consequences: "Satu daftar gabungan menuntut register pintu (opsi B) beserta sinkronisasi status, tidak sepadan untuk 1,5 komplain per bulan." Kalimat itu mencampur dua hal yang berbeda. Daftar gabungan yang **hanya dibaca** tidak menuntut register baru dan tidak menuntut sinkronisasi status apa pun, sebab tiap register tetap jadi sumber kebenaran statusnya sendiri dan agregator tidak pernah menulis. Penolakan **opsi C** (satu register gabungan) tetap berlaku utuh dengan alasannya sendiri: kosakata dan wewenang kedua register memang berbeda, dan hanya 13 sampai 29 persen baris kode kedua fitur yang ada semata-mata karena belahan itu.

### Status dokumen yang jadi pijakan

Pijakan utamanya ADR 0114 (⚠️ diterima, irisan 1 mendarat) dan pembacaan kode langsung di `origin/main` pada 22 September 2026, ditambah pengukuran prod di atas. [[REF - Kepemilikan Data]] belum memuat baris untuk kedua register komplain; pendaftarannya masuk daftar task, bukan prasyarat ADR ini.

## Decision

**1. Satu tabel BACA terpusat untuk pengaju, leader, dan SPV. Register tetap dua.** Halaman baru di modul Marketing memuat riwayat komplain gudang dan komplain mutu dalam satu tabel berkolom sama. Halaman `/warehouse/komplain` dan `/quality/komplain` tetap ada dan tetap jadi tempat unit penanganannya bekerja.

**2. Dirakit agregator di employee-service, bukan di frontend.** Endpoint baru bersaudara dengan `/pengajuan/ringkasan` dan memakai ulang seluruh mekanismenya: registri sumber, identitas pemanggil disalin sekali sebelum pemanggilan paralel, batas waktu per sumber, dan balasan `{data, degraded}` yang membedakan "sumber gagal" dari "tidak ada baris". Alasannya sama dengan ADR 0114 keputusan 6: employee-service sudah memegang registri lintas modul dan bukan pemilik register komplain mana pun.

**3. Sumbunya RIWAYAT PENGAJUAN, bukan antrean keputusan, jadi endpointnya sendiri.** Tidak ditumpangkan ke `/pengajuan/antrean` milik ADR 0114. Antrean berisi yang menunggu keputusan **pembaca**; tabel ini berisi yang menunggu keputusan **orang lain** atas pengajuan pembaca. Mencampurnya membuat satu tabel menjawab dua pertanyaan yang berlawanan, dan kolom Tahap milik ADR 0114 akan berarti dua hal sekaligus.

**4. Tujuh kolom, dan tiap kolom WAJIB terisi untuk kedua register.** Unit, Perihal, Pesanan, Toko, Diajukan oleh, Status, Menunggu sejak. Urut dari yang paling lama menggantung, bukan per unit. Unit dan Status jadi penyaring di toolbar, dan nomor pesanan bisa dicari. Kolom **Perihal diisi satu kalimat jadi oleh agregator**, bukan dirakit layar dari field tiap register (ADR 0114 keputusan 2).

Aturannya dinyatakan terang karena ADR 0114 keputusan 1 sudah pernah tergelincir di titik ini: ia menetapkan kolom Nilai lalu menemukan bentuk ringkas sumbernya tak membawa nominal apa pun untuk ketujuh kategorinya, sehingga kolomnya kosong seluruhnya. **Sebuah kolom hanya boleh masuk bila kedua register benar-benar mengisinya**, dan itu diperiksa dengan membaca model, bukan menduga dari nama. Yang tidak memenuhi syarat tidak dihapus dari produk, melainkan dibuat terisi atau dipindah ke `Sheet`.

⛔ **Kolom Toko karena itu MENUNTUT keputusan 4 [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] mendarat lebih dulu.** Diukur di `origin/main` 2026-09-22: `KomplainGudang` punya `shop_id`, sedangkan `QualityComplaint` tidak punya sama sekali dan `order_ref`-nya masih teks bebas. Menghapus kolomnya bukan jawaban, sebab bagi pemegang toko justru "toko mana" yang paling menentukan; dan menambalnya di agregator dengan menebak dari `order_ref` juga bukan, sebab itu melahirkan sumber kebenaran kedua soal komplain ini milik toko mana, yang dilarang keputusan 6 di bawah. Yang benar: registernya yang memiliki identitas itu, diisi server dari data pesanan, lalu agregator tinggal membacanya. **Halaman ini tidak tayang sebelum itu.**

⚠️ **Produk dan SKU sengaja TIDAK jadi kolom, dan ini bukan kekurangan data yang bisa ditambal.** Register gudang bekerja per **pesanan**, register QC per **item**, dan pembagian itu ditetapkan keputusan 4 ADR 0103. Satu pesanan bisa memuat beberapa produk, jadi satu sel "Produk" untuk baris gudang akan berbohong. Keduanya muncul di `Sheet` detail, yang memang berganti bentuk per unit (keputusan 8), bersama atribusi packer untuk baris gudang dan tingkat keparahan untuk baris QC.

⚠️ Dua kolom lain tetap bercatatan yang wajib ikut ke layar. **Pesanan**: nilai gudang diverifikasi ke `fulfillment_orders` saat komplain dibuat sementara nilai QC masih teks bebas, jadi keduanya belum sama kuat sampai keputusan 4 itu mendarat. **Diajukan oleh**: register gudang selalu mengisi `dilaporkan_oleh`, sedangkan `metadata.created_by` register QC bisa kosong untuk komplain yang dibuat lewat token layanan tanpa header identitas, jadi baris tanpa pengaju ditangani eksplisit dan tidak dirender sebagai sel kosong yang terbaca seperti data hilang.

**5. Kosakata status dipetakan DI AGREGATOR ke satu himpunan**: `menunggu`, `diproses`, `tuntas`, `ditolak`. Nilai asli tiap register tetap dikirim di field terpisah untuk keperluan detail dan penelusuran, sebab membuangnya membuat baris mustahil dicocokkan kembali ke sumbernya. Register gudang tidak punya padanan `menunggu` selain `baru`, dan pemetaannya ditulis eksplisit, bukan diturunkan dari kemiripan nama.

**6. Cakupan baris = cakupan register asalnya. Agregator tidak melebarkan dan tidak menyempitkan.** Ia meneruskan identitas pemanggil dan menerima apa pun yang tiap register putuskan, sehingga gerbang tetap milik service asalnya.

   ⛔ Konsekuensinya wajib ditangani di layar, bukan didiamkan: karena baris QC belum bisa disempitkan per toko, tabel **wajib menandai per baris** apakah ia milik pembaca. Tanpa penanda itu pemegang toko membaca komplain brand lain seolah miliknya sendiri, dan itu lebih buruk daripada dua tabel terpisah yang jelas cakupannya. Polanya sudah ada di sistem ini: antrean Tinjau Setoran Live Support mengirim `boleh_putus` per baris. Penanda ini **dicabut** begitu keputusan 4 ADR 0103 mendarat dan baris QC punya identitas toko.

**7. Agregator TIDAK PERNAH MENULIS.** Seluruh aksi dari tabel ini menembak endpoint keputusan milik register asalnya, dengan gerbangnya sendiri. Perhitungan KPI packing tidak tersentuh sama sekali, termasuk aturan bahwa komplain `ditolak` tidak dihitung, yang tetap tinggal di warehouse-service.

**8. Detail dibuka lewat `Sheet`, dan tiap unit wajib menyatakan di mana detailnya dibuka** sebelum barisnya boleh masuk tabel (ADR 0114 keputusan 5). Baris gudang membuka sheet tindak lanjut yang sudah ada; baris QC membuka dialog validasi yang sudah ada berikut bukti ulasannya. Unit yang kelak ditambahkan tanpa jalur detail tidak membuka apa pun, sebab baris yang diam lebih baik daripada panel yang dijamin gagal.

**9. Dua prasyarat dikerjakan LEBIH DULU dan bukan bagian tabel ini**: paket `marketing_akuntoko_pemegang` dipasang ke pemegang toko, dan kabar inbox saat ulasan bintang rendah masuk dihidupkan (ADR 0099 keputusan 8, belum ada kodenya). Keduanya sudah diputuskan ADR lain, jadi ADR ini tidak memutuskannya ulang, hanya menyatakan urutannya. Tanpa keduanya tabel ini kosong bagi audiens utamanya.

**10. Rekap berangka dan bahan laporan TIDAK dibangun sekarang.** Tabel ini melayani dua dari empat kegunaan yang dinyatakan pemilik proses: menagih yang menggantung, dan mencari cepat per pesanan. Dua sisanya menuntut bentuk angka per periode, bukan daftar baris, dan diputuskan setelah register benar-benar terisi. Memutuskannya sekarang berarti merancang rekap di atas nol dokumen.

**11. Tidak ada sumber kebenaran ketiga.** Tabel ini tidak menyimpan apa pun. Angka ringkasnya, bila kelak dibutuhkan di beranda portal, mengambil dari agregator yang sama, bukan dari salinan.

## Consequences

**Yang membaik.** Pengaju tidak lagi membuka dua halaman milik dua departemen lain untuk tahu nasib laporannya. Leader dan SPV mendapat satu tempat untuk menagih yang menggantung, dan untuk pertama kalinya riwayat komplain bisa dicari per nomor pesanan tanpa tahu lebih dulu keluhannya milik unit mana.

**Yang memburuk, dan diterima sadar.**

- Agregator memegang adapter untuk kedua register, jadi perubahan field di salah satunya dapat merusak kolom Perihal **tanpa satu pun galat**. Penjaganya test kontrak yang mengurai rekaman respons sungguhan tiap register, bukan tiruan struct. Ini kelas kegagalan yang sudah menggigit di sini: uji yang memalsukan sumbernya tetap hijau sementara tak satu pun baris benar-benar ditarik.
- Satu halaman lagi yang dibaca dua audiens, jadi ia wajib menggerbangi dirinya sendiri dan tiap aksinya, seperti `/quality/komplain`. Rutenya **tidak** dimasukkan ke daftar rute privat per departemen, sebab daftar itu mengalihkan siapa pun tanpa peran departemen bersangkutan dan justru akan mengunci marketing dari halamannya sendiri.
- Sampai penanda per baris di keputusan 6 dicabut, pembaca tetap melihat baris QC brand lain. Yang dipertukarkan kerahasiaan antar brand demi satu tabel yang berguna bagi satu tim, dan itu meneruskan pertukaran yang sudah diterima ADR 0103 keputusan 11.

**Yang tidak berubah.** Siapa berwenang memutuskan apa. Dua register, dua daur hidup, dua konsumen KPI. Cara mengajukan komplain, yang tetap satu pintu dari baris ulasan.

**Yang tetap terbuka.** Rekap berangka dan bahan laporan. Pendaftaran kedua register di [[REF - Kepemilikan Data]]. Pengajuan komplain mutu di luar baris ulasan marketplace, yang masih menunggu keputusan 4 ADR 0103.

**Konsekuensi deploy.** Endpoint agregat baru berarti **backend sebelum frontend**. Ia memanggil warehouse-service dan membaca register QC di databasenya sendiri, jadi blok `employee-service` di compose kemungkinan butuh env base URL warehouse; penambahan env menuntut `docker compose up -d --force-recreate`, bukan `restart`. **Tanpa kategori inbox baru** untuk tabel ini sendiri, jadi notification-service tidak perlu naik karenanya; kabar ulasan bintang rendah di keputusan 9 adalah pekerjaan terpisah yang memang menambah kategori dan menuntut notification-service naik lebih dulu. **Tanpa migrasi data**, sebab kedua register nol dokumen, dan itu pula yang membuat perubahan kontrak apa pun di sekitarnya semurah sekarang.

## Dokumen Terkait

- [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] — pola tabel seragam, agregator, dan aturan "tiap kategori menyatakan di mana detailnya dibuka"
- [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] — satu pintu pengajuan, dan alasan penolakan daftar gabungan yang dikoreksi di sini
- [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] — dua register, tanpa register ketiga, dan notifikasi ulasan bintang rendah
- [[ADR - 0107 Alat Kerja Pemegang Akun Toko lewat Izin Posisi akuntoko]] — paket izin yang belum dipasang
- [[REF - Alur Persetujuan]] — kelas cacat "wewenang tanpa kemampuan melihat"
- [[Microservices - Employee Service]] · [[Microservices - Warehouse Service]] · [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[APP - Web ERP]] · [[CORE - RBAC dan Permission Set]] · [[Sales - ICC Account Manager Mapping]] · [[REF - Kepemilikan Data]]
